# Research: Pesquisa: Melhores SITES e PORTAIS WEB para busca de jurisprudencias brasileiras.

CONTEXTO: Queremos criar um Agente ADK que faca buscas de jurisprudencia DIRETAMENTE nesses sites via web fetch/scraping. NAO estamos buscando APIs - ja temos a API do STJ dados abertos funcionando.

FOCO DA PESQUISA:
1. Portais oficiais dos tribunais (STF, STJ, TRFs 1-5, TJs estaduais, TST, TRTs)
2. Sites de agregadores de jurisprudencia
3. Bibliotecas juridicas online
4. Bases de dados de decisoes

CRITERIOS DE AVALIACAO PARA CADA SITE:
1. Qualidade do HTML/estrutura da pagina (facilidade de parsing)
2. Completude dos dados (inteiro teor, ementa, votos, numero do processo, data, relator)
3. Cobertura temporal (decisoes de que periodo?)
4. Sistema de busca (aceita operadores booleanos? filtros?)
5. Limitacoes de acesso (captcha, rate limiting, login obrigatorio?)
6. Formato das URLs (previsivel, permite deep linking?)

OUTPUT ESPERADO:
Lista dos 10-15 melhores sites para busca de jurisprudencia, com:
- URL do portal de busca
- Tribunais cobertos
- Tipo de dados disponiveis
- Qualidade para web scraping/fetching
- Motivacao para incluir/excluir como fonte no Agente ADK

**Generated:** 2026-01-13T02:05:44.838667
**Model:** gemini-2.5-flash

---

## Melhores SITES e PORTAIS WEB para busca de jurisprudências brasileiras para Web Scraping

### Key Findings

*   A maioria dos portais oficiais dos tribunais superiores e federais oferece sistemas de busca com filtros avançados e operadores booleanos, disponibilizando o inteiro teor dos julgados.
*   O STJ já possui uma API de dados abertos para jurisprudência, conforme o contexto fornecido pelo usuário.
*   Portais como o STF, STJ, TST, e vários TJs (TJMG, TJRJ, TJSP) e TRFs (TRF1, TRF2, TRF3, TRF4) permitem a consulta de acórdãos, súmulas, ementas e, em alguns casos, decisões monocráticas.
*   A cobertura temporal varia significativamente entre os tribunais; o TST, por exemplo, disponibiliza processos desde 1998.
*   Alguns tribunais, como o TJSP, explicitam que o acesso à pesquisa de jurisprudência é gratuito e não requer cadastro.
*   A menção de "qualidade HTML/estrutura da página" e "formato das URLs (previsível, permite deep linking?)" não é diretamente detalhada nas buscas, mas a existência de sistemas de "pesquisa avançada" e "filtros" sugere uma estrutura mais organizada, potencialmente facilitando o parsing.
*   Limitações de acesso, como captchas ou rate limiting, não são consistentemente documentadas nos resultados de busca para todos os portais, embora o TJSP mencione acesso ininterrupto via navegadores.

### Technical Specifications and Evaluation

| URL do Portal de Busca | Tribunais Cobertos | Tipo de Dados Disponíveis | Qualidade para Web Scraping/Fetching (Inferido) | Motivação para Incluir/Excluir |
| :--------------------- | :----------------- | :------------------------- | :--------------------------------------------- | :------------------------------- |
| **STF: Pesquisa de Jurisprudência** | STF | Inteiro teor de acórdãos, súmulas, repercussão geral, informativos. | Alta (Sistema de busca avançada com dicas de pesquisa, organização por temas e informativos). URLs para resultados podem ser estáveis se baseadas em IDs de processo. | Essencial para jurisprudência constitucional de tribunais superiores. Incluir para abrangência. |
| **STJ: Pesquisa de Jurisprudência** | STJ, Tribunal Federal de Recursos (TFR) | Acórdãos, súmulas, decisões monocráticas, Informativo de Jurisprudência, Pesquisa Pronta. | Alta (A API de dados abertos já é utilizada, mas o portal web complementa a estratégia. Sistema de busca com filtros). | Essencial para jurisprudência infraconstitucional de tribunais superiores. Incluir, mesmo com API, para cobertura de dados não acessíveis via API. |
| **TRF1: Pesquisa de Jurisprudência** | TRF1 (AC, AM, AP, BA, DF, GO, MA, MT, PA, PI, RO, RR, TO) | Pesquisa simples e avançada com campos específicos (classe, órgão julgador, relator), operadores lógicos e moduladores. | Média a Alta (Múltiplos filtros sugerem estrutura de dados consistente; potencial para URLs previsíveis). | Abrangência regional da Justiça Federal. Incluir. |
| **TRF2: Portal de Jurisprudência** | TRF2, TRU e Turmas Recursais da 2ª Região (RJ, ES) | Julgados dos órgãos da Justiça Federal da 2ª Região. Portal de Jurisprudência e-Proc TRF2, TRU e Turmas Recursais. | Média a Alta (Pesquisa por termo, URL direta para o portal de jurisprudência). | Abrangência regional da Justiça Federal. Incluir. |
| **TRF3: Pesquisa de Jurisprudência** | TRF3 (SP, MS) | Acórdãos, Súmulas do TRF3, Jurisprudência Unificada do CJF e TNU. | Média (Informado contato para jurisprudência, sugere portal funcional). | Abrangência regional da Justiça Federal. Incluir. |
| **TRF4: Portal Unificado da Justiça Federal da 4ª Região** | TRF4, JFRS, JFSC, JFPR | Pesquisa processual judicial e administrativa. Seção de Jurisprudência. | Média a Alta (Portal unificado com critérios de pesquisa específicos, embora mencione que algumas funções podem ser prejudicadas se Javascript desativado). | Abrangência regional da Justiça Federal. Incluir. |
| **TRF5: Portal da Justiça Federal da 5ª Região** | TRF5 (AL, CE, PB, PE, RN, SE) | Julgados [cite: 31, no contexto da busca pelo CJF]. | Média (Informação direta do portal de busca não foi encontrada na pesquisa atual; inferido que a estrutura seja similar a outros TRFs). | Abrangência regional da Justiça Federal. Incluir. |
| **TJMG: Consulta de Jurisprudência** | TJMG | Inteiro teor das decisões, acórdãos, súmulas, precedentes qualificados. | Alta (Diversos filtros: número do processo, palavras-chave, órgão julgador, relator, classe, assunto, data de publicação/julgamento, referência legislativa). | Abrangência estadual. Incluir devido à completude e riqueza de filtros. |
| **TJRJ: Consulta Jurisprudência** | TJRJ | Decisões judiciais, acórdãos, sentenças. Busca por campos específicos (origem, ano, competência, ramo do direito), operadores E/OU/ADJ. | Alta (Pesquisa avançada com múltiplos campos e operadores booleanos. "Inteiro Teor" disponível. Detalhes sobre a estrutura da busca e operadores lógicos são bem documentados). | Abrangência estadual. Incluir. |
| **TJSP: Jurisprudência e Banco de Sentenças** | TJSP | Jurisprudências de Segundo Grau (acórdãos), Banco de Sentenças. | Alta (Consulta completa com busca textual à íntegra, filtros por classe, órgão julgador, data. Acesso gratuito e sem cadastro). | Abrangência estadual e volume de processos. Incluir. |
| **TST: Pesquisa de Jurisprudência** | TST, TRTs (filtrável) | Acórdãos, decisões monocráticas, súmulas, orientações jurisprudenciais, precedentes normativos. Permite uso de aspas para pesquisa exata. Base de dados desde 1998. | Alta (Ferramenta atualizada, busca rápida e intuitiva, filtros refinados, exportação de documentos). | Essencial para jurisprudência trabalhista. Incluir. |
| **CJF: Pesquisa de Jurisprudência Unificada** | Justiça Federal (TRFs e Turmas Recursais) | Jurisprudência Unificada, Jurisprudência da TNU, Jurisprudência Administrativa CJF. | Alta (Portal unificado, sugere estrutura padronizada para coleta de dados de diversas fontes da Justiça Federal). | Agregador oficial da Justiça Federal. Incluir para dados de TRFs e TNU. |
| **Dizer o Direito: Buscador de Jurisprudência** | STF, STJ | Julgados selecionados e comentados, informativos, com entendimento do STF e STJ. | Média (Plataforma com filtros por categoria e ordenação. Atualizações semanais. É um agregador curado, não um tribunal primário, o que pode influenciar a completude de *todos* os julgados, mas a qualidade do conteúdo é alta). | Excluir como fonte primária para *scraping* de *todos* os julgados devido à natureza curada. Pode ser útil para referências e entendimentos sumarizados, mas não para coleta em massa. |
| **CNJ: Infojuris** | CNJ | Acórdãos proferidos pelo Plenário do CNJ, Informativo de Jurisprudência, Regimento Interno Anotado. | Média (Sistema de consulta específico para acórdãos do CNJ). | Incluir para decisões do Conselho Nacional de Justiça, relevante para a administração e regulamentação do judiciário. |

### Data Conflicts / Uncertainties

*   **Cobertura Temporal do Dizer o Direito**: Embora um resultado cite "julgado em 01/12/2025" para o Dizer o Direito, isso parece ser um erro de data ou um exemplo futuro, visto que a data atual é janeiro de 2026. A plataforma afirma atualizações semanais.
*   **Qualidade do HTML para Scraping**: A avaliação da "qualidade do HTML/estrutura da página" e "formato das URLs" é inferencial com base nas descrições de funcionalidades de busca. Sem acesso direto para inspeção, a facilidade real de parsing e a previsibilidade das URLs podem variar.
*   **Limitações de Acesso**: As informações sobre captchas e rate limiting não são consistentemente detalhadas para todos os portais. O TJSP menciona "acesso gratuito" e sem cadastro, o que sugere menor restrição, mas não exclui outras barreiras.

### Source Index

1.  Como buscar jurisprudência no TRF-1 | Entenda o passo a passo | Blog da JUIT. (2023-03-31).
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHT2Idt29T0EZTf0f1mHwG-2wFjw_ol8sbbfd6BgegIV0W3uZSmDl9mEfA_brPmGf61tzO4jSmTCwWxHF8x5pC6jaorlV_DP0ppiqEAk0_fCQYhnkPlA5jbQzmTfrJCiX-1M1PnkHSphQ==](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHT2Idt29T0EZTf0f1mHwG-2wFjw_ol8sbbfd6BgegIV0W3uZSmDl9mEfA_brPmGf61tzO4jSmTCwWxHF8x5pC6jaorlV_DP0ppiqEAk0_fCQYhnkPlA5jbQzmTfrJCiX-1M1PnkHSphQ==)
2.  Jurisprudência TJRJ: como buscar decisões de forma rápida - Jurídico AI. (2025-11-05).
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMdZ9qEGe97mxOQlNlGfUtCVWRDZoNfXvWUUqCuHXTUDvoaypPGGk32JRGQpl8gP93SKUaH8EqSGI1Uhw6CwAuQHoNkpHLuLDrI5G57VwCojudFwkk_CuZCLv-eiQwOaYeRIaPUbtTltNJjNcvnCybi6r](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMdZ9qEGe97mxOQlNlGfUtCVWRDZoNfXvWUUqCuHXTUDvoaypPGGk32JRGQpl8gP93SKUaH8EqSGI1Uhw6CwAuQHoNkpHLuLDrI5G57VwCojudFwkk_CuZCLv-eiQwOaYeRIaPUbtTltNJjNcvnCybi6r)
3.  Pesquisa de Jurisprudência - Supremo Tribunal Federal.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGP1EBMHzdG-pRG6nmUQYSHxLqyWmb8novOX8KIfw54nPeGBF4uQUuzJ9KPg6Y5VECBpcjG-gt8xximbkbvdUXE6WjoKosutDL10l3zIprjSFFz7behVhl_xpu3_OWI1hI6dil2](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGP1EBMHzdG-pRG6nmUQYSHxLqyWmb8novOX8KIfw54nPeGBF4uQUuzJ9KPg6Y5VECBpcjG-gt8xximbkbvdUXE6WjoKosutDL10l3zIprjSFFz7behVhl_xpu3_OWI1hI6dil2)
4.  Consulta de Jurisprudência | Portal TJMG.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqEv1m3zybdh7vGQLF-9tYriJRVDNGKs5wiryF9kq9iSAd7vc3D3jlU7506tzhgghamDAnblnoNJcT0VYPpsQPzicTmM482bmEybvXD7-PnqeL16HrMN_wHPA_-t2I-Bjqzq-w-224q1SUD_evd6IQr7j96-HkT8rjqnoiGsrsPKdyZVP03gViPw==](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqEv1m3zybdh7vGQLF-9tYriJRVDNGKs5wiryF9kq9iSAd7vc3D3jlU7506tzhgghamDAnblnoNJcT0VYPpsQPzicTmM482bmEybvXD7-PnqeL16HrMN_wHPA_-t2I-Bjqzq-w-224q1SUD_evd6IQr7j96-HkT8rjqnoiGsrsPKdyZVP03gViPw==)
5.  Pesquisa de Jurisprudência - STJ.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHV5yw_dNdpMrc3LcP3JV1Ed7h07vknhBi10xa79Dy0yTatXYpVcG7TVpmjXM6oCWcVEsLZ7UZRkIoIo_thY7gW0xPPM1jiOKUlwv8y4H8U34NIqD8ujEN_NvbYsu_6SF2zAHIYcbES51GnRrO7xSfIr5sBKo_T9apaXC7MIVKZy3R_lNFzL99rlUSAnqVM-6XC6S2tj7zdrktIT_-xokZSLJkJ4O4O9kf2Jkg==](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHV5yw_dNdpMrc3LcP3JV1Ed7h07vknhBi10xa79Dy0yTatXYpVcG7TVpmjXM6oCWcVEsLZ7UZRkIoIo_thY7gW0xPPM1jiOKUlwv8y4H8U34NIqD8ujEN_NvbYsu_6SF2zAHIYcbES51GnRrO7xSfIr5sBKo_T9apaXC7MIVKZy3R_lNFzL99rlUSAnqVM-6XC6S2tj7zdrktIT_-xokZSLJkJ4O4O9kf2Jkg==)
6.  Passo a passo para consultar jurisprudência no TJSP - Jurídico AI. (2025-11-05).
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMJWEC7qlann8eE-tTsZyNdg5bsM138yWPdEIT5MgpeE22wuUD_5ObQUlaC51hHZQQM4a02VaTXwT33rA7KH2ng0dK_eXLKyokqNqQFNB30oyzeHlbLhddDxcB_yuxLt0WMGekbyCJUBvbKlVOjb1RQ9Xwfr](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMJWEC7qlann8eE-tTsZyNdg5bsM138yWPdEIT5MgpeE22wuUD_5ObQUlaC51hHZQQM4a02VaTXwT33rA7KH2ng0dK_eXLKyokqNqQFNB30oyzeHlbLhddDxcB_yuxLt0WMGekbyCJUBvbKlVOjb1RQ9Xwfr)
7.  Jurisprudência no TJMG, como pesquisar? | Guia Completo | Blog da JUIT. (2023-08-02).
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHogwYhnadu-792zPG0fdzzYs17_sJmMGfAXIqJ4yhvRfyJq4UbedvBVRQlNyzcKDdgP4w_ISJVarcgHi97GKRq4ncbJrSejMTHkIxDKYnXSzyX9Tq9xRaJp9vF40Lff9B8NHS3Xqp9](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHogwYhnadu-792zPG0fdzzYs17_sJmMGfAXIqJ4yhvRfyJq4UbedvBVRQlNyzcKDdgP4w_ISJVarcgHi97GKRq4ncbJrSejMTHkIxDKYnXSzyX9Tq9xRaJp9vF40Lff9B8NHS3Xqp9)
8.  Consulta de Jurisprudência | Justiça Federal - 2ª Região. (2025-01-22).
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQES5YdcHDx5notX4ZtMY7IerGUImvNrgZtLwSXwllayjbc4ccb5aKymV9Vtrlz1DlEQgMmQJDYk7wA6UctuE_vzy_Di2U0j2OwPoiUTX4W0m-fphw34AIvosoKHxMba6Cso7UU1TtA4GvdP3G4-LcJQBtN8zQ3FJubrsqtJ6TfP5w==](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQES5YdcHDx5notX4ZtMY7IerGUImvNrgZtLwSXwllayjbc4ccb5aKymV9Vtrlz1DlEQgMmQJDYk7wA6UctuE_vzy_Di2U0j2OwPoiUTX4W0m-fphw34AIvosoKHxMba6Cso7UU1TtA4GvdP3G4-LcJQBtN8zQ3FJubrsqtJ6TfP5w==)
9.  Jurisprudência | Portal TJMG.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFgdYJMnwugo5oK2RH8Sl6IhRfPVteCQzudi5NUA_KK0PYzz9BWKIIA1Z8EOUXf9Zm_jQzzLW1cJRM7IXnUuiB2apWXCyvN85nwBbwTH0-P5QKNFcv8yF2WEGaY9gUuX5jPEhh9o72PABJZEH_jw==](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFgdYJMnwugo5oK2RH8Sl6IhRfPVteCQzudi5NUA_KK0PYzz9BWKIIA1Z8EOUXf9Zm_jQzzLW1cJRM7IXnUuiB2apWXCyvN85nwBbwTH0-P5QKNFcv8yF2WEGaY9gUuX5jPEhh9o72PABJZEH_jw==)
10. Busca Jurisprudência - TRF3.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4IySUKne9YwsAkug515c-3xgOhyw5iZvfw91LxL5DlKJn78scLO2kfCj9aKwLhXNYf52rgge8fekzqKr9TL0LtqBtbQtYeseL_lfz2EcS2OAk352kv-LNm-mLqYr_0sDkKQ==](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4IySUKne9YwsAkug515c-3xgOhyw5iZvfw91LxL5DlKJn78scLO2kfCj9aKwLhXNYf52rgge8fekzqKr9TL0LtqBtbQtYeseL_lfz2EcS2OAk352kv-LNm-mLqYr_0sDkKQ==)
11. Jurisprudência - Buscador Dizer o Direito.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjcJ27lYmBzlpYAE6MrX1jwnBTJOaEXpx44EzkRoi8GgM-pD-TmSzZ_iQttHjQeitf-8gAc6cxXMPkdCmhs10CJzY0JTNu2_heLAMXGKtgBMNhZ-tFXbXa-1th8B3UMawC4a8TEpa644n_nO5i-w==](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjcJ27lYmBzlpYAE6MrX1jwnBTJOaEXpx44EzkRoi8GgM-pD-TmSzZ_iQttHjQeitf-8gAc6cxXMPkdCmhs10CJzY0JTNu2_heLAMXGKtgBMNhZ-tFXbXa-1th8B3UMawC4a8TEpa644n_nO5i-w==)
12. Jurisprudência | Portal CNJ.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJlzsb3L_5W4KLlz2cGVtWOj-qj3W61OI18LgATBG-RL6r41lru9Uqq9WPKUb91MdqugOXON0ET7W1S_umBS_40r8tdJESxNaTFhusujFw9-nRU4L49pYaNngJY3QogND-uGetJK8xa8hUnIrj](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJlzsb3L_5W4KLlz2cGVtWOj-qj3W61OI18LgATBG-RL6r41lru9Uqq9WPKUb91MdqugOXON0ET7W1S_umBS_40r8tdJESxNaTFhusujFw9-nRU4L49pYaNngJY3QogND-uGetJK8Irj)
13. Pesquisa de jurisprudência - TST.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFONTcCfOzsXPj0gaoGIKPIRnJSnCMOcXQ7Cgggbi59VXEK32HJgNNLe9dVj2WRZ9dyBiob7-EFHM5B_HpAPtJGuLi5qtnbwvbqOUJ75APUPv8mLmocXyFhDMrI4X7Vi-zQf3BfG0EcBzCMafI=](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFONTcCfOzsXPj0gaoGIKPIRnJSnCMOcXQ7Cgggbi59VXEK32HJgNNLe9dVj2WRZ9dyBiob7-EFHM5B_HpAPtJGuLi5qtnbwvbqOUJ75APUPv8mLmocXyFhDMrI4X7Vi-zQf3BfG0EcBzCMafI=)
14. Dúvidas - Jurisprudência - Tribunal de Justiça.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJSAuUKVgGClf0smy4yWTg6tNDfNEfMyXjVi_Q6vDqbHEeYJN-NynsGoCLaVZU4NMeXBpIfXwotAHMtJjls4Px8E_0YbOSZ6_d_XKACMFlmMoMZaqlCqv0T-Cb5H_k2QvMurNrKbM-YhNr5QfaAZPnOp0T1C08gglPQVrZLPyFUeq_VKWDCGe11NvTAu7kxknqEbI=](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJSAuUKVgGClf0smy4yWTg6tNDfNEfMyXjVi_Q6vDqbHEeYJN-NynsGoCLaVZU4NMeXBpIfXwotAHMtJjls4Px8E_0YbOSZ6_d_XKACMFlmMoMZaqlCqv0T-Cb5H_k2QvMurNrKbM-YhNr5QfaAZPnOp0T1C08gglPQVrZLPyFUeq_VKWDCGe11NvTAu7kxknqEbI=)
15. Jurisprudência | Justiça Federal - 2ª Região.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-6PdCWeFbKN7XP_v6nH49xsqqTIBBRcV0-VZBHOJzjztJ7JR0WVVsPQYalo78oKjgGjpJL2utQDttDxwrJbtepr8Q-0yaqLoL027DArTPVBEkJ06biLiDrHs2r3fIdQhssFPTrsSscOSZVaPuK4lrwP-UMUnabOxYKvY=](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-6PdCWeFbKN7XP_v6nH49xsqqTIBBRcV0-VZBHOJzjztJ7JR0WVVsPQYalo78oKjgGjpJL2utQDttDxwrJbtepr8Q-0yaqLoL027DArTPVBEkJ06biLiDrHs2r3fIdQhssFPTrsSscOSZVaPuK4lrwP-UMUnabOxYKvY=)
16. Consulta de jurisprudência no TJRJ, como fazer? | Guia | Blog da JUIT. (2023-08-03).
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnCbuka437nRdYyEUpI-YtbKrZzhIF_oIH5eEYNOqJkWWLvt59untdytJnaSeyrlnYtW2BK-RdxRd_cRTqzSy3wiqJLRwH5XxVjozZokdkRMZCdd4IH0jcEl5_PybkhoOz0HhTFm-q](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnCbuka437nRdYyEUpI-YtbKrZzhIF_oIH5eEYNOqJkWWLvt59untdytJnaSeyrlnYtW2BK-RdxRd_cRTqzSy3wiqJLRwH5XxVjozZokdkRMZCdd4IH0jcEl5_PybkhoOz0HhTFm-q)
17. Tema 280 do STF – Busca domiciliar sem mandado – necessária justificativa - situação de flagrante — Tribunal de Justiça do Distrito Federal e dos Territórios - TJDFT. (2025-10-24).
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFlsibvmCz40LorhD6n-4FLk5ka6YvtDTpxIVW2hq8YrLR3qIgtTO0ekuoyc8uxsd3YxgGbJ6bd0T_RMHh_WOMexAiuon1SUMOVp9INNiy9Q6X35Ir979CyYfk9NbLpoEdVv-E8FDWuYT0jWhlNKIdoaeNE_9w7FmwrGpgtfTQu1vqDyVOne2QFtiqD8t8Ov6h5ta5MXwHogafeleJ2XkB3Gan-aO0ECXIR72feZCKRA3OQZ1BEW7YoYRgubeckXG2XItSZZ5BEMm8EUUvwOC5sqk4P6EongiMDz4gP4JVpPASdOz_hcTw7su4pDuWMhoCVMwJ0x61O_3Gszb84DkDyHfYllwySeFG3_llaoKIFvFOXPMgR5jFq65rZSnCLkHTpT0NkzCELx6jHsm7M7HmdME3N83GIbWnWlDs=](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFlsibvmCz40LorhD6n-4FLk5ka6YvtDTpxIVW2hq8YrLR3qIgtTO0ekuoyc8uxsd3YxgGbJ6bd0T_RMHh_WOMexAiuon1SUMOVp9INNiy9Q6X35Ir979CyYfk9NbLpoEdVv-E8FDWuYT0jWhlNKIdoaeNE_9w7FmwrGpgtfTQu1vqDyVOne2QFtiqD8t8Ov6h5ta5MXwHogafeleJ2XkB3Gan-aO0ECXIR72feZCKRA3OQZ1BEW7YoYRgubeckXG2XItSZZ5BEMm8EUUvwOC5sqk4P6EongiMDz4gP4JVpPASdOz_hcTw7su4pDuWMhoCVMwJ0x61O_3Gszb84DkDyHfYllwySeFG3_llaoKIFvFOXPMgR5jFq65rZSnCLkHTpT0NkzCELx6jHsm7M7HmdME3N83GIbWnWlDs=)
18. Consulta Jurisprudência.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFMJL5PkykNWAc6FevIikprGFzeVklv30Dfs-vtb28hNWa5AFVa3oZyoXe6G4MwQ6J2-fzZiUwUAUyrLnyKZk0m3SkmhmFh_wCrIqa0ryU3rJEv7DsWzyGO2mEg-9fbqDsGmbqT](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFMJL5PkykNWAc6FevIikprGFzeVklv30Dfs-vtb28hNWa5AFVa3oZyoXe6G4MwQ6J2-fzZiUwUAUyrLnyKZk0m3SkmhmFh_wCrIqa0ryU3rJEv7DsWzyGO2mEg-9fbqDsGmbqT)
19. TST atualiza ferramenta de busca para facilitar pesquisa de jurisprudência - YouTube. (2019-07-01).
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLf3NQMTfTYUq6Iers5V5GT95kpgWmsSTcGbiATdrrpEvJMZqZBfEGfkaGAaaMmp0-uDpJ82JBU7tkxuXCh76g3j_LttSHquJ3ys7491ZOprN9exWeHCEp3LC0QATfKHT2kjVpJA8=](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLf3NQMTfTYUq6Iers5V5GT95kpgWmsSTcGbiATdrrpEvJMZqZBfEGfkaGAaaMmp0-uDpJ82JBU7tkxuXCh76g3j_LttSHquJ3ys7491ZOprN9exWeHCEp3LC0QATfKHT2kjVpJA8=)
20. STJ - Superior Tribunal de Justiça.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBzljt-3-15xscltCA9egLFMcpXbn7lZCoD-nQFEk3UBkcsRf1q7AMN5GtMIe3Y4msKvRCv41hPhCSXXJlbAjUd-4s_i7gHtIjmStgVz-VHgCD](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBzljt-3-15xscltCA9egLFMcpXbn7lZCoD-nQFEk3UBkcsRf1q7AMN5GtMIe3Y4msKvRCv41hPhCSXXJlbAjUd-4s_i7gHtIjmStgVz-VHgCD)
21. Buscador Dizer o Direito: Encontre Jurisprudência Comentada do STF e do STJ e muito mais.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGVHhf5RNj7-_iKje6A2fqupjAvh7_bZBNgHB_-fhevsjZI8GIKaRK_QUQlNkR4KWKK8jC7CBJaPYtjU-rgQ_A0v6IN2ALfe3nr1csfyYKSgAwXAW4n5clbHwY2DJUnJxg=](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGVHhf5RNj7-_iKje6A2fqupjAvh7_bZBNgHB_-fhevsjZI8GIKaRK_QUQlNkR4KWKK8jC7CBJaPYtjU-rgQ_A0v6IN2ALfe3nr1csfyYKSgAwXAW4n5clbHwY2DJUnJxg=)
22. Pesquisa por Jurisprudência - TJMG.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBMbb4Jr5SwFtpzUnwgHJ6al_7JtU5JkRUmDVSst6SHUrm-k1siBEwQX38b7DqcMvKK5pANJz4IvMciZ-IEM8dNuNVdRBaqwipqqKlcE-Cv9boNkWrBJSiTWm_oeZ9blFoEHyHPuFGovrBC7Rtmc06mA__MJt9FUY=](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBMbb4Jr5SwFtpzUnwgHJ6al_7JtU5JkRUmDVSst6SHUrm-k1siBEwQX38b7DqcMvKK5pANJz4IvMciZ-IEM8dNuNVdRBaqwipqqKlcE-Cv9boNkWrBJSiTWm_oeZ9blFoEHyHPuFGovrBC7Rtmc06mA__MJt9FUY=)
23. Consulta à Jurisprudência - Tribunal de Justiça do Estado do Rio de Janeiro.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENfxd2pJJeWscnvr7qGa7p09fcCHATVrR6dp7T4d6WEn8lEzuf1OXUDtGpThzvTQaYVjk-krHJt6xBwQEhe5fW6qGNlQMB1XyIB3k2naPludPgJVtVsnZEjfM3nxYoeCSAARMALOplbcNSPGpW8m_ytZ1Z3lMa7Q==](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENfxd2pJJeWscnvr7qGa7p09fcCHATVrR6dp7T4d6WEn8lEzuf1OXUDtGpThzvTQaYVjk-krHJt6xBwQEhe5fW6qGNlQMB1XyIB3k2naPludPgJVtVsnZEjfM3nxYoeCSAARMALOplbcNSPGpW8m_ytZ1Z3lMa7Q==)
24. Consultas de Jurisprudência - E-SAJ - Tribunal de Justiça.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjvLgVxe2v37Rlu2sV62CP3P_ctT6a-9dTb9LSdP8HcWgMKStbKcSXpYOhM8g9V291IY2__f8oZcSdqA2OF3e7WIjuzchG3cjhBwpuzQpIbx3DYWr9fVdEdiQcimKX-e97-_0TdAII](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjvLgVxe2v37Rlu2sV62CP3P_ctT6a-9dTb9LSdP8HcWgMKStbKcSXpYOhM8g9V291IY2__f8oZcSdqA2OF3e7WIjuzchBwpuzQpIbx3DYWr9fVdEdiQcimKX-e97-_0TdAII)
25. Jurisprudência e Banco de Sentenças HML - Tribunal de Justiça.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFaEacxwKY0NrX_N23ySb-_OjQ14p11kCisTjSYW3IphvNMbpc2sxXQMD92mxIYOCX49pyvS_JhwrJLAy-tQF8EZxv1Q9lT3STjXgW8mVDvBOAY7Z29_04FlWd0QAPcwNWd](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFaEacxwKY0NrX_N23ySb-_OjQ14p11kCisTjSYW3IphvNMbpc2sxXQMD92mxIYOCX49pyvS_JhwrJLAy-tQF8EZxv1Q9lT3STjXgW8mVDvBOAY7Z29_04FlWd0QAPcwNWd)
26. Como fazer pesquisa de Jurisprudência no TJSP? Passo-a-Passo | Blog da JUIT. (2022-12-23).
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1RPksI_efQvpW3-B7W4Pi6APcVuqtUQUgkf9XI7W_3S51QIWzaGFMcNsH1WlZHD7mFqe3sOAbYL__xI_HmUBGRLRV33_d1EFOP3PwjXwIqTiVuAZIH8lfZBAs5Sx31Ls9qOM_oJeQJCJZa90Aznvy](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1RPksI_efQvpW3-B7W4Pi6APcVuqtUQUgkf9XI7W_3S51QIWzaGFMcNsH1WlZHD7mFqe3sOAbYL__xI_HmUBGRLRV33_d1EFOP3PwjXwIqTiVuAZIH8lfZBAs5Sx31Ls9qOM_oJeQJCJZa90Aznvy)
27. sistema de jurisprudência - TJRJ.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHH63R5NjwtFz8SHokotVo6K3wVU2m2zqE3SyOiUAArs8NTCxedmVzyLvCZAR-Q-yKEIuWgrVVHZNYe2TO0jlYnE3mD0R5SFCDCBtWfrqO9HHpgYK7sCjc31V9ycpmRNbK8SqhZ1PLLEbFjqwt7Egk-3KxXrHmsVLCPjSGybFuXFG2pn1y2JeNzOYySq2cHnW-c4gmksIkCgioy3xBkdYj9rjWKUOOJ](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHH63R5NjwtFz8SHokotVo6K3wVU2m2zqE3SyOiUAArs8NTCxedmVzyLvCZAR-Q-yKEIuWgrVVHZNYe2TO0jlYnE3mD0R5SFCDCBtWfrqO9HHpgYK7sCjc31V9ycpmRNbK8SqhZ1PLLEbFjqwt7Egk-3KxXrHmsVLCPjSGybFuXFG2pn1y2JeNzOYySq2cHnW-c4gmksIkCgioy3xBkdYj9rjWKUOOJ)
28. Informativo STF | Portal STF. (2024-09-01).
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEr0-8V3kA2zn0MfWU_FCvjPOO4QcS5zovX3EIXi-vKf1874Cf5PzzvlN9ITqg3NAMHPRTSalZk-Tj7_juFQ9FtZMhC3HBXi3fzRKoDHlT-RLvbdk92SxhkBEwKf29swjnRsPhuF4X5aPrSK5jvY5xXE5UapaKqQDmaplvduZTP](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEr0-8V3kA2zn0MfWU_FCvjPOO4QcS5zovX3EIXi-vKf1874Cf5PzzvlN9ITqg3NAMHPRTSalZk-Tj7_juFQ9FtZMhC3HBXi3fzRKoDHlT-RLvbdk92SxhkBEwKf29swjnRsPhuF4X5aPrSK5jvY5xXE5UapaKqQDmaplvduZTP)
29. TRF4.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGy5qSmcySZauH4jI4uCHV9_fCQvcDYtgxz0aQK9QVPCJXfNJeGoO_YHlYao794jRfzCZRBmKkJQBCJvutKAPRi3wfySABJ5qB-Zh1XD-TAPMc8bg==](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGy5qSmcySZauH4jI4uCHV9_fCQvcDYtgxz0aQK9QVPCJXfNJeGoO_YHlYao794jRfzCZRBmKkJQBCJvutKAPRi3wfySABJ5qB-Zh1XD-TAPMc8bg==)
30. Jurisprudência - TST.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxNFOPSFX-_P9oLJVq6zP0dqA8dIJam7njkSkrbC3N6KfKA92Dn4zS5ZLmP_-orTtE0xtTpakNTbvRaj-9-oNY0kOYzO9QEiN5rf6gH587XKj3VePN50Y2ooQu7UibYEM=](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxNFOPSFX-_P9oLJVq6zP0dqA8dIJam7njkSkrbC3N6KfKA92Dn4zS5ZLmP_-orTtE0xtTpakNTbvRaj-9-oNY0kOYzO9QEiN5rf6gH587XKj3VePN50Y2ooQu7UibYEM=)
31. Página Inicial - Conselho da Justiça Federal — Conselho da Justiça Federal.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIe7zHTFV2trDGNUXWvHAwzwaommJbVjB0pRO0EmGEARgHLwQ57OK_db2IegJbHMFnwdfeXb_lPKR34XYadDNBYT9n-Ybx8VK5ngBNrbb0OG8vpgcw](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIe7zHTFV2trDGNUXWvHAwzwaommJbVjB0pRO0EmGEARgHLwQ57OK_db2IegJbHMFnwdfeXb_lPKR34XYadDNBYT9n-Ybx8VK5ngBNrbb0OG8vpgcw)
32. TRF3.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRQNkbNGQOSjBl8sSexpbbIs3sKbhqtd4nghwIsArs4oEmGE-f83wD7JNE-vwtpe6P9LrVzw1YZ3AUEei24clAkjizGYUnzKM6uPRM_gODnrmtkA==](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRQNkbNGQOSjBl8sSexpbbIs3sKbhqtd4nghwIsArs4oEmGE-f83wD7JNE-vwtpe6P9LrVzw1YZ3AUEei24clAkjizGYUnzKM6uPRM_gODnrmtkA==)
33. Seção Judiciária de Mato Grosso do Sul: Internet.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDfouC26ZY-w6xFkb74yMwOlmjKgRc1mjmyImpBd5p8ifr4O1nPUNhaOBv5UOOqeEH-Oy9e6xBjmlUGSvzQdC7rFhAUQpN7nJ0skPFMnDC2ZgQgA==](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDfouC26ZY-w6xFkb74yMwOlmjKgRc1mjmyImpBd5p8ifr4O1nPUNHAOBv5UOOqeEH-Oy9e6xBjmlUGSvzQdC7rFhAUQpN7nJ0skPFMnDC2ZgQgA==)
34. Jurisprudência - Tribunal de Justiça do Estado do Rio de Janeiro - TJRJ.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1zNtHmn_ETAYMOa-uRI6Dvuo5cHB4zB5_Ezr5f6m96vbN-KG9FRVgpEVZHMzAr5Px0ZJxsWWn3EWHIePsJOHn4CGAQZYjAlG9ji7fCXy4pvHGVVQ0logKm7BqD5B5RU3w2GlV7DAgE68p1oYM4N1lYM4=](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1zNtHmn_ETAYMOa-uRI6Dvuo5cHB4zB5_Ezr5f6m96vbN-KG9FRVgpEVZHMzAr5Px0ZJxsWWn3EWHIePsJOHn4CGAQZYjAlG9ji7fCXy4pvHGVVQ0logKm7BqD5B5RU3w2GlV7DAgE68p1oYM4N1lYM4=)
35. Como pesquisar a jurisprudência trabalhista - Professor Fabiano Coelho - YouTube. (2025-07-12).
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLMjRzcOAe59h2YdXfmW_sdzDbDmWDTaZdtW5nY2Nad9Pkah5TfGlqME7HBtyuZra01kTpAyp7j3aPedWITHN5pZoiZFsbb2FC1oC3hFg_vl0MOB25iy1Gs9gh-LZk7_dXS--rvWA=](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLMjRzcOAe59h2YdXfmW_sdzDbDmWDTaZdtW5nY2Nad9Pkah5TfGlqME7HBtyuZra01kTpAyp7j3aPedWITHN5pZoiZFsbb2FC1oC3hFg_vl0MOB25iy1Gs9gh-LZk7_dXS--rvWA=)
36. TST - TRT/RJ.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEh9ntYyENC4T_nVNFHNZc5gHsHk02Cildy6MrZEkWADMdywFskf7wP7h3xHFzMOP5gicHFuPNXPmBSo8efaV8at3_RKDLbjYxJbpCNjXzY1AUDqb3Zhw==](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEh9ntYyENC4T_nVNFHNZc5gHsHk02Cildy6MrZEkWADMdywFskf7wP7h3xHFzMOP5gicHFuPNXPmBSo8efaV8at3_RKDLbjYxJbpCNjXzY1AUDqb3Zhw==)
37. Como Pesquisar - FALCÃO - Sistema de busca de jurisprudência.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBTimWKTmUta5nWqL69LdQrqifL36FyN2xuDsRsITUpKrceZ_VAW5kGceXtkRcYEcKP710bfCWR9kgWCNI6ejtuvwpJ1bzQz35f7r6t_RCdMhZWwKcEFtSP0hxQ1ZQ7YWF1KD5oAXSEP7dL5OpXOjGUpUjSbUg8FDSXTAc](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBTimWKTmUta5nWqL69LdQrqifL36FyN2xuDsRsITUpKrceZ_VAW5kGceXtkRcYEcKP710bfCWR9kgWCNI6ejtuvwpJ1bzQz35f7r6t_RCdMhZWwKcEFtSP0hxQ1ZQ7YWF1KD5oAXSEP7dL5OpXOjGUpUjSbUg8FDSXTAc)
38. Internet: Seção Judiciária de São Paulo.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEr_FWWGqfyLKXibMmOjGkjECqZzYAnyj28-KXxzq1uQuEhOp-f0r17-mZu3dY3Ts184yHuh_1i1tyPyGBx3_rRqLk1dxxA7fQ85FP5GOJTZx6GtA==](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEr_FWWGqfyLKXibMmOjGkjECqZzYAnyj28-KXxzq1uQuEhOp-f0r17-mZu3dY3Ts184yHuh_1i1tyPyGBx3_rRqLk1dxxA7fQ85FP5GOJTZx6GtA==)
39. COMO CONSULTAR PROCESSO DE MINAS GERAIS - TJMG - YouTube. (2023-02-21).
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNYzzs-hZympBTGUFYCccsK6jWRB0s-k9uJV-GRC2a4VRlU0gxwCvRPQQC8Auy9pN5dlWEnpn-mpMoiNt9NFula7EHi-yAqWxFVaBX3URAxIzoCrVZf-KilMXFmk3_VeBtFVOEAVE=](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHNYzzs-hZympBTGUFYCccsK6jWRB0s-k9uJV-GRC2a4VRlU0gxwCvRPQQC8Auy9pN5dlWEnpn_mpMoiNt9NFula7EHi-yAqWxFVaBX3URAxIzoCrVZf-KilMXFmk3_VeBtFVOEAVE=)
40. HOW TO CONSULT THE TRF1 (1ST REGION) PROCESS - YouTube. (2023-06-21).
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9JMhxFrj_hWRe3351M8LxBdr31F-D6C8ttuIyVApW4JkZTy4tL2rCW9fzLdyKIDmbITrjVAUTOeoiMGKOgb-VH1Rx2vnEWeVZgxZIrNZdba9ibQHKxxy-41ARWu3SDLq3k8-r6rA=](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF9JMhxFrj_hWRe3351M8LxBdr31F-D6C8ttuIyVApW4JkZTy4tL2rCW9fzLdyKIDmbITrjVAUTOeoiMGKOgb-VH1Rx2vnEWeVZgxZIrNZdba9ibQHKxxy-41ARWu3SDLq3k8-r6rA=)
41. TRT2.
    [https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFintlY21lZIpYiaD7Co5h-Yp_81bXA_1EWeQjenpeLgsA-RIAk9ciOx95jQ6xh8O65zxqZGbz-MWJ7PKZ2NXGPJ1xImxaFo_DvJF0KHfNXQc0FjA==](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFintlY21lZIpYiaD7Co5h-Yp_81bXA_1EWeQjenpeLgsA-RIAk9ciOx95jQ6xh8O65zxqZGbz-MWJ7PKZ2NXGPJ1xImxaFo_DvJF0KHfNXQc0FjA==)

---

## Metadata

### Search Queries Executed

### Sources
- [juit.com.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHT2Idt29T0EZTf0f1mHwG-2wFjw_ol8sbbfd6BgegIV0W3uZSmDl9mEfA_brPmGf61tzO4jSmTCwWxHF8x5pC6jaorlV_DP0ppiqEAk0_fCQYhnkPlA5jbQzmTfrJCiX-1M1PnkHSphQ==)
- [stf.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGP1EBMHzdG-pRG6nmUQYSHxLqyWmb8novOX8KIfw54nPeGBF4uQUuzJ9KPg6Y5VECBpcjG-gt8xximbkbvdUXE6WjoKosutDL10l3zIprjSFFz7behVhl_xpu3_OWI1hI6dil2)
- [stj.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHV5yw_dNdpMrc3LcP3JV1Ed7h07vknhBi10xa79Dy0yTatXYpVcG7TVpmjXM6oCWcVEsLZ7UZRkIoIo_thY7gW0xPPM1jiOKUlwv8y4H8U34NIqD8ujEN_NvbYsu_6SF2zAHIYcbES51GnRrO7xSfIr5sBKo_T9apaXC7MIVKZy3R_lNFzL99rlUSAnqVM-6XC6S2tj7zdrktIT_-xokZSLJkJ4Oa9kf2Jkg==)
- [juit.com.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHogwYhnadu-792zPG0fdzzYs17_sJmMGfAXIqJ4yhvRfyJq4UbedvBVRQlNyzcKDdgP4w_ISJVarcgHi97GKRq4ncbJrSejMTHkIxDKYnXSzyX9Tq9xRaJp9vF40Lff9B8NHS3Xqp9)
- [tst.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFONTcCfOzsXPj0gaoGIKPIRnJSnCMOcXQ7Cgggbi59VXEK32HJgNNLe9dVj2WRZ9dyBiob7-EFHM5B_HpAPtJGuLi5qtnbwvbqOUJ75APUPv8mLmocXyFhDMrI4X7Vi-zQf3BfG0EcBzCMafI=)
- [tjsp.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGjvLgVxe2v37Rlu2sV62CP3P_ctT6a-9dTb9LSdP8HcWgMKStbKcSXpYOhM8g9V291IY2__f8oZcSdqA2OF3e7WIjuzchG3cjhBwpuzQpIbx3DYWr9fVdEdiQcimKX-e97-_0TdAII)
- [tjmg.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEFgdYJMnwugo5oK2RH8Sl6IhRfPVteCQzudi5NUA_KK0PYzz9BWKIIA1Z8EOUXf9Zm_jQzzLW1cJRM7IXnUuiB2apWXCyvN85nwBbwTH0-P5QKNFcv8yF2WEGaY9gUuX5jPEhh9o72PABJZEH_jw==)
- [trf2.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-6PdCWeFbKN7XP_v6nH49xsqqTIBBRcV0-VZBHOJzjztJ7JR0WVVsPQYalo78oKjgGjpJL2utQDttDxwrJbtepr8Q-0yaqLoL027DArTPVBEkJ06biLiDrHs2r3fIdQhssFPTrsSscOSZVaPuK4lrwP-UMUnabOxYKvY=)
- [stj.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGBzljt-3-15xscltCA9egLFMcpXbn7lZCoD-nQFEk3UBkcsRf1q7AMN5GtMIe3Y4msKvRCv41hPhCSXXJlbAjUd-4s_i7gHtIjmStgVz-VHgCD)
- [tjsp.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFaEacxwKY0NrX_N23ySb-_OjQ14p11kCisTjSYW3IphvNMbpc2sxXQMD92mxIYOCX49pyvS_JhwrJLAy-tQF8EZxv1Q9lT3STjXgW8mVDvBOAY7Z29_04FlWd0QAPcwNWd)
- [stf.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEr0-8V3kA2zn0MfWU_FCvjPOO4QcS5zovX3EIXi-vKf1874Cf5PzzvlN9ITqg3NAMHPRTSalZk-Tj7_juFQ9FtZMhC3HBXi3fzRKoDHlT-RLvbdk92SxhkBEwKf29swjnRsPhuF4X5aPrSK5jvY5xXE5UapaKqQDmaplvduZTP)
- [trf4.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGy5qSmcySZauH4jI4uCHV9_fCQvcDYtgxz0aQK9QVPCJXfNJeGoO_YHlYao794jRfzCZRBmKkJQBCJvutKAPRi3wfySABJ5qB-Zh1XD-TAPMc8bg==)
- [tst.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFxNFOPSFX-_P9oLJVq6zP0dqA8dIJam7njkSkrbC3N6KfKA92Dn4zS5ZLmP_-orTtE0xtTpakNTbvRaj-9-oNY0kOYzO9QEiN5rf6gH587XKj3VePN50Y2ooQu7UibYEM=)
- [cjf.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFIe7zHTFV2trDGNUXWvHAwzwaommJbVjB0pRO0EmGEARgHLwQ57OK_db2IegJbHMFnwdfeXb_lPKR34XYadDNBYT9n-Ybx8VK5ngBNrbb0OG8vpgcw)
- [trf3.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGRQNkbNGQOSjBl8sSexpbbIs3sKbhqtd4nghwIsArs4oEmGE-f83wD7JNE-vwtpe6P9LrVzw1YZ3AUEei24clAkjizGYUnzKM6uPRM_gODnrmtkA==)
- [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFLf3NQMTfTYUq6Iers5V5GT95kpgWmsSTcGbiATdrrpEvJMZqZBfEGfkaGAaaMmp0-uDpJ82JBU7tkxuXCh76g3j_LttSHquJ3ys7491ZOprN9exWeHCEp3LC0QATfKHT2kjVpJA8=)
- [tjsp.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGJSAuUKVgGClf0smy4yWTg6tNDfNEfMyXjVi_Q6vDqbHEeYJN-NynsGoCLaVZU4NMeXBpIfYwotAHMtJjls4Px8E_0YbOSZ6_d_XKACMFlmMoMZaqlCqv0T-Cb5H_k2QvMurNrKbM-YhNr5QfaAZPnOp0T1C08gglPQVrZLPyFUeq_VKWDCGe11NvTAu7kxknqEbI=)
- [juridico.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEMJWEC7qlann8eE-tTsZyNdg5bsM138yWPdEIT5MgpeE22wuUD_5ObQUlaC51hHZQQM4a02VaTXwT33rA7KH2ng0dK9_eXLKyokqNqQFNB30oyzeHlbLhddDxcB_yuxLt0WMaGekbyCJUBvbKlVOjb1RQ9Xwfr)
- [juit.com.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1RPksI_efQvpW3-B7W4Pi6APcVuqtUQUgkf9XI7W_3S51QIWzaGFMcNsH1WlZHD7mFqe3sOAbYL__xI_HmUBGRLRV33_d1EFOP3PwjXwIqTiVuAZIH8lfZBAs5Sx31Ls9qOM_oJeQJCJZa90Aznvy)
- [tjrj.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHH63R5NjwtFz8SHokotVo6K3wVU2m2zqE3SyOiUAArs8NTCxedmVzyLvCZAR-Q-yKEIuWgrVVHZNYe2TOwjlYnE3mD0R5SFCDCBtWfrqO9HHpgYK7sCjc31V9ycpmRNbK8SqhZ1PLLEbFjqwt7Egk-3KxXrHmsVLCPjSGybFuXFG2pn1y2JeNzOYySq2cHnW-c4gmksIkCgioy3xBkdYj9rjWKUOOJ)
- [trf2.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQES5YdcHDx5notX4ZtMY7IerGUImvNrgZtLwSXwllayjbc4ccb5aKymV9Vtrlz1DlEQgMmQJDYk7wA6UctuE_vzy_Di2U0j2OwPoiUTX4W0m-fphw34AIvosoKHxMba6Cso7UU1TtA4GvdP3G4-LcJQBtN8zQ3FJubrsqtJ6TfP5w==)
- [trf3.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF4IySUKne9YwsAkug515c-3xgOhyw5iZvfw91LxL5DlKJn78scLO2kfCj9aKwLhXNYf52rgge8fekzqKr9TL0LtqBtbQtYeseL_lfz2EcS2OAk352kv-LNm-mLqYr_0sDkKQ==)
- [jfms.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGDfouC26ZY-w6xFkb74yMwOlmjKgRc1mjmyImpBd5p8ifr4O1nPUNhaOBv5UOOqeEH-Oy9e6xBjmlUGSvzQdC7rFhAUQpN7nJ0skPFMnDC2ZgQgA==)
- [tjmg.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGqEv1m3zybdh7vGQLF-9tYriJRVDNGKs5wiryF9kq9iSAd7vc3D3jlU7506tzhgghamDAnblnoNJcT0VYPpsQPzicTmM482bmEybvXD7-PnqeL16HrMN_wHPA_-t2I-Bjqzq-w-224q1SUD_evd6IQr7j96-HkT8rjqnoiGsrsPKdyZVP03gViPw==)
- [tjmg.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFBMbb4Jr5SwFtpzUnwgHJ6al_7JtU5JkRUmDVSst6SHUrm-k1siBEwQX38b7DqcMvKK5pANJz4IvMciZ-IEM8dNuNVdRBaqwipqqKlcE-Cv9boNkWrBJSiTWm_oeZ9blFoEHyHPuFGovrBC7Rtmc06mA__MJt9FUY=)
- [juridico.ai](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMdZ9qEGe97mxOQlNlGfUtCVWRDZoNfXvWUUqCuHXTUDvoaypPGGk32JRGQpl8gP93SKUaH8EqSGI1Uhw6CwAuQHoNkpHLuLDrI5G57VwCojudWfwkk_CuZCLv-eiQwOaYeRIaPUbtTltNJjNcvnCybi6r)
- [juit.com.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnCbuka437nRdYyEUpI-YtbKrZzhIF_oIH5eEYNOqJkWWLvt59untdytJnaSeyrlnYtW2BK-RdxRd_cRTqzSy3wiqJLRwH5XxVjozZokdkRMZCdd4IH0jcEl5_PybkhoOz0HhTFm-q)
- [tjrj.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQENfxd2pJJeWscnvr7qGa7p09fcCHATVrR6dp7T4d6WEn8lEzuf1OXUDtGpThzvTQaYVjk-krHJt6xBwQEhe5fW6qGNlQMB1XyIB3k2naPludPgJVtVsnZEjfM3nxYoeCSAARMALOplbcNSPGpW8m_ytZ1Z3lMa7Q==)
- [tjrj.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE1zNtHmn_ETAYMOa-uRI6Dvuo5cHB4zB5_Ezr5f6m96vbN-KG9FRVgpEVZHMzAr5Px0ZJxsWWn3EWHIePsJOHn4CGAQZYjAlG9ji7fCXy4pvHGVVQ0logKm7BqD5B5RU3w2GlV7DAgE68p1oYM4N1lYM4=)
- [buscadordizerodireito.com.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHjcJ27lYmBzlpYAE6MrX1jwnBTJOaEXpx44EzkRoi8GgM-pD-TmSzZ_iQttHjQeitf-8gAc6cxXMPkdCmhs10CJzY0JTNu2_heLAMXGKtgBMNhZ-tFXbXa-1th8BfUMawC4a8TEpa644n_nO5i-w==)
- [buscadordizerodireito.com.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGVHhf5RNj7-_iKje6A2fqupjAvh7_bZBNgHB_-fhevsjZI8GIKaRK_QUQlNkR4KWKK8jC7CBJaPYtjU-rgQ_A0v6IN2ALfe3nr1csfyYKSgAwXAW4n5clbHwY2DJUnJxg=)
- [cnj.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJlzsb3L_5W4KLlz2cGVtWOj-qj3W61OI18LgATBG-RL6r41lru9Uqq9WPKUb91MdqugOXON0ET7W1S_umBS_40r8tdJESxNaTFhusujFw9-nRU4L49pYaNngJY3QogND-uGetJK8xa8hUnIrj)
