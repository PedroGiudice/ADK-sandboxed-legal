"""Visual Verifier - ADK Agent para verificacao visual automatizada.

Este agente verifica paginas web usando multiplas ferramentas:
- Playwright: Screenshots e E2E automatizado
- Compare: Diff visual entre screenshots
- Console/Network: Verificacao de erros

Uso:
    cd adk-agents && adk run visual_verifier
"""

import asyncio
import base64
import hashlib
from pathlib import Path
from datetime import datetime
from io import BytesIO
from typing import Optional

from google.adk.agents import Agent

# ============================================================================
# TOOL: Compare Screenshots
# ============================================================================

try:
    from PIL import Image, ImageChops
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


def _compare_images(current_path: str, baseline_path: str, threshold: float = 0.95) -> dict:
    """Compara dois screenshots."""
    if not HAS_PIL:
        return {
            "match": False,
            "similarity": 0.0,
            "message": "Erro: Pillow nao instalado"
        }

    try:
        img_current = Image.open(current_path).convert("RGB")
        img_baseline = Image.open(baseline_path).convert("RGB")

        if img_current.size != img_baseline.size:
            img_current = img_current.resize(img_baseline.size, Image.Resampling.LANCZOS)

        diff = ImageChops.difference(img_current, img_baseline)
        diff_data = list(diff.getdata())
        total_diff = sum(sum(pixel) for pixel in diff_data)
        max_diff = 255 * 3 * len(diff_data)
        similarity = 1.0 - (total_diff / max_diff)

        match = similarity >= threshold
        return {
            "match": match,
            "similarity": round(similarity, 4),
            "message": f"Similaridade: {similarity:.1%}"
        }

    except Exception as e:
        return {"match": False, "similarity": 0.0, "message": str(e)}


def _get_image_hash(image_path: str) -> Optional[str]:
    """Retorna hash MD5 de uma imagem."""
    path = Path(image_path)
    if not path.exists():
        return None
    try:
        return hashlib.md5(path.read_bytes()).hexdigest()[:8]
    except Exception:
        return None


# ============================================================================
# TOOL: Playwright Browser
# ============================================================================

try:
    from playwright.async_api import async_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


async def _take_screenshot_async(url: str, output_path: str) -> dict:
    """Captura screenshot de uma URL."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=output_path, full_page=True)
            return {"success": True, "path": output_path, "message": f"Screenshot salvo: {output_path}"}
        except Exception as e:
            return {"success": False, "path": None, "message": str(e)}
        finally:
            await browser.close()


def _take_screenshot(url: str, output_path: str) -> dict:
    """Wrapper sync para screenshot."""
    if not HAS_PLAYWRIGHT:
        return {"success": False, "path": None, "message": "Playwright nao instalado"}
    return asyncio.run(_take_screenshot_async(url, output_path))


async def _check_console_async(url: str) -> dict:
    """Verifica erros no console."""
    errors = []
    warnings = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        page.on("console", lambda msg: (
            errors.append(msg.text) if msg.type == "error"
            else warnings.append(msg.text) if msg.type == "warning"
            else None
        ))
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)
            return {
                "success": True,
                "errors": errors,
                "warnings": warnings,
                "has_errors": len(errors) > 0
            }
        except Exception as e:
            return {"success": False, "errors": [str(e)], "warnings": [], "has_errors": True}
        finally:
            await browser.close()


def _check_console(url: str) -> dict:
    """Wrapper sync para console check."""
    if not HAS_PLAYWRIGHT:
        return {"success": False, "errors": ["Playwright nao instalado"], "warnings": [], "has_errors": True}
    return asyncio.run(_check_console_async(url))


async def _check_network_async(url: str) -> dict:
    """Verifica erros de rede."""
    failed = []
    total = [0]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        def on_response(response):
            total[0] += 1
            if not response.ok:
                failed.append({"url": response.url, "status": response.status})

        page.on("response", on_response)
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            return {
                "success": True,
                "total_requests": total[0],
                "failed_requests": failed,
                "has_failures": len(failed) > 0
            }
        except Exception as e:
            return {"success": False, "total_requests": 0, "failed_requests": [], "has_failures": True}
        finally:
            await browser.close()


def _check_network(url: str) -> dict:
    """Wrapper sync para network check."""
    if not HAS_PLAYWRIGHT:
        return {"success": False, "total_requests": 0, "failed_requests": [], "has_failures": True}
    return asyncio.run(_check_network_async(url))


# ============================================================================
# AGENT TOOLS
# ============================================================================

BASELINES_DIR = Path(__file__).parent / "baselines"
SCREENSHOTS_DIR = Path(__file__).parent / "screenshots"

BASELINES_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


def verify_page(
    url: str,
    page_name: str,
    threshold: float = 0.95,
    check_console: bool = True,
    check_network: bool = True
) -> dict:
    """Verifica uma pagina web completamente.

    Executa verificacao visual (screenshot comparison) e funcional
    (console errors, network errors).

    Args:
        url: URL da pagina a verificar
        page_name: Nome identificador da pagina (ex: "login", "dashboard")
        threshold: Limiar de similaridade visual (0.0 a 1.0)
        check_console: Se deve verificar erros no console
        check_network: Se deve verificar erros de rede

    Returns:
        Dict com resultado completo da verificacao
    """
    results = {
        "passed": True,
        "page_name": page_name,
        "url": url,
        "timestamp": datetime.now().isoformat(),
        "summary": []
    }

    current_path = SCREENSHOTS_DIR / f"{page_name}_current.png"
    baseline_path = BASELINES_DIR / f"{page_name}_baseline.png"

    # 1. Screenshot
    screenshot = _take_screenshot(url, str(current_path))
    if not screenshot["success"]:
        results["passed"] = False
        results["summary"].append(f"ERRO: {screenshot['message']}")
        return results

    # 2. Comparacao visual
    if baseline_path.exists():
        visual = _compare_images(str(current_path), str(baseline_path), threshold)
        if not visual["match"]:
            results["passed"] = False
            results["summary"].append(f"VISUAL: REGRESSAO - {visual['message']}")
        else:
            results["summary"].append(f"VISUAL: OK ({visual['similarity']:.1%})")
    else:
        results["summary"].append("VISUAL: Baseline ausente (use update_baseline)")

    # 3. Console
    if check_console:
        console = _check_console(url)
        if console["has_errors"]:
            results["passed"] = False
            results["summary"].append(f"CONSOLE: {len(console['errors'])} erros")
        else:
            results["summary"].append("CONSOLE: OK")

    # 4. Network
    if check_network:
        network = _check_network(url)
        if network["has_failures"]:
            results["passed"] = False
            results["summary"].append(f"NETWORK: {len(network['failed_requests'])} falhas")
        else:
            results["summary"].append(f"NETWORK: OK ({network['total_requests']} requests)")

    return results


def update_baseline(url: str, page_name: str) -> dict:
    """Atualiza o baseline de uma pagina.

    Captura novo screenshot e salva como baseline de referencia.

    Args:
        url: URL da pagina
        page_name: Nome identificador da pagina

    Returns:
        Dict com status da operacao
    """
    current_path = SCREENSHOTS_DIR / f"{page_name}_current.png"
    baseline_path = BASELINES_DIR / f"{page_name}_baseline.png"

    screenshot = _take_screenshot(url, str(current_path))
    if not screenshot["success"]:
        return {"success": False, "message": f"Erro: {screenshot['message']}"}

    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_path.write_bytes(current_path.read_bytes())

    return {
        "success": True,
        "message": f"Baseline salvo: {baseline_path}",
        "hash": _get_image_hash(str(baseline_path))
    }


def list_baselines() -> dict:
    """Lista todos os baselines existentes.

    Returns:
        Dict com lista de baselines e seus hashes
    """
    baselines = []

    if BASELINES_DIR.exists():
        for file in BASELINES_DIR.glob("*_baseline.png"):
            page_name = file.stem.replace("_baseline", "")
            baselines.append({
                "page_name": page_name,
                "path": str(file),
                "hash": _get_image_hash(str(file))
            })

    return {
        "count": len(baselines),
        "baselines": baselines,
        "baselines_dir": str(BASELINES_DIR)
    }


def quick_check(url: str) -> dict:
    """Verificacao rapida de uma URL (sem comparacao visual).

    Apenas verifica console e network.

    Args:
        url: URL a verificar

    Returns:
        Dict com resultado
    """
    results = {"passed": True, "url": url, "checks": []}

    console = _check_console(url)
    if console["has_errors"]:
        results["passed"] = False
        results["checks"].append(f"CONSOLE: {len(console['errors'])} erros")
        for err in console["errors"][:3]:
            results["checks"].append(f"  - {err[:100]}")
    else:
        results["checks"].append("CONSOLE: OK")

    network = _check_network(url)
    if network["has_failures"]:
        results["passed"] = False
        results["checks"].append(f"NETWORK: {len(network['failed_requests'])} falhas")
    else:
        results["checks"].append(f"NETWORK: OK ({network['total_requests']} requests)")

    return results


# ============================================================================
# AGENT DEFINITION
# ============================================================================

root_agent = Agent(
    name="visual_verifier",
    model="gemini-2.5-flash",
    instruction="""Voce e um agente de verificacao visual para aplicacoes web.

Suas capacidades:
1. verify_page: Verificacao completa (visual + console + network)
2. update_baseline: Atualiza screenshot de referencia
3. list_baselines: Lista baselines existentes
4. quick_check: Verificacao rapida sem comparacao visual

Workflow tipico:
1. Primeiro, use list_baselines para ver o que ja existe
2. Para nova pagina, use update_baseline para criar referencia
3. Para verificar, use verify_page e reporte o resultado
4. Para check rapido, use quick_check

Sempre reporte resultados de forma clara:
- PASSOU: todas verificacoes OK
- FALHOU: liste exatamente o que falhou e por que
""",
    tools=[
        verify_page,
        update_baseline,
        list_baselines,
        quick_check
    ]
)
