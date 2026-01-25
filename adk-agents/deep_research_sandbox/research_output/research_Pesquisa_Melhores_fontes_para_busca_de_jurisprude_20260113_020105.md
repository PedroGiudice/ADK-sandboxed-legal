# Research: Pesquisa: Melhores fontes para busca de jurisprudencias brasileiras com acesso programatico (API/fetching).

CRITERIOS DE AVALIACAO:
1. Acessibilidade tecnica: APIs publicas, endpoints REST, possibilidade de web scraping legal
2. Completude dos dados: inteiro teor, numero do processo, data, relator, ementa, votos
3. Cobertura: tribunais incluidos (STF, STJ, TRFs, TJs estaduais, TST, TRT)
4. Qualidade juridica: dados confiaveis para uso em pecas processuais
5. Gratuidade vs pago: disponibilidade sem autenticacao paga

FONTES A INVESTIGAR:
- Portais oficiais dos tribunais (STF, STJ, TRFs, TJs)
- JusBrasil (limitacoes de acesso programatico)
- LexML Brasil
- DataJud CNJ
- APIs governamentais
- Outras fontes abertas

OUTPUT ESPERADO:
Lista ranqueada de fontes com:
- Nome da fonte
- URL/endpoint
- Tipo de acesso (API, scraping, browser automation)
- Dados disponiveis
- Limitacoes
- Motivacao para uso/nao uso

**Generated:** 2026-01-13T02:00:27.448281
**Model:** gemini-2.5-flash

---

## Melhores Fontes para Busca de Jurisprudências Brasileiras com Acesso Programático

### Key Findings

*   O **DataJud CNJ** emerge como a principal fonte pública para acesso programático a *metadados* de processos judiciais em âmbito nacional, cobrindo a maioria dos tribunais brasileiros. Sua API é gratuita e não exige autenticação atualmente.
*   **Tribunais individuais** como TJDFT oferecem APIs públicas para jurisprudência, mas a cobertura é restrita ao próprio tribunal.
*   O **STF** disponibiliza dados de decisões através do programa "Corte Aberta" via BigQuery e download, com dados mais recentes potencialmente pagos, mas o acesso direto ao *inteiro teor* de acórdãos via API REST não é explicitamente detalhado para automação.
*   **Fontes comerciais** como Judit.io oferecem APIs para consulta de jurisprudência em tempo real com ampla cobertura, indicando ser uma solução para a completude de dados e abrangência de tribunais.
*   A obtenção do *inteiro teor* da jurisprudência de forma programática e gratuita em escala nacional permanece um desafio, sendo o DataJud CNJ limitado a metadados.

### Technical Specifications

| Fonte             | URL/Endpoint Principal                                     | Tipo de Acesso             | Dados Disponíveis (via API/scraping)                                                                                                                  | Gratuidade vs Pago |
| :---------------- | :--------------------------------------------------------- | :------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------- |
| **DataJud CNJ**   | `datajud.cnj.jus.br/api-publica` (documentação na wiki do CNJ) | API Pública (REST)         | Metadados processuais: Número do processo, tribunal, classe, assunto, partes, movimentações, datas importantes, status do processo. | Gratuito           |
| **TJDFT**         | `www.tjdft.jus.br/transparencia/tecnologia-da-informacao-e-comunicacao/dados-abertos/webservice-ou-api` | API Pública (REST)         | Acórdãos e decisões: Número do processo, data de autuação, competência, classe, órgão julgador, segredo de justiça, movimentações.     | Gratuito           |
| **STF (Corte Aberta)** | `basedosdados.org/dataset/br-stf-corte-aberta` | BigQuery, Download (SQL, Python, R) | Ano, classe, número do processo, relator, link do processo, subgrupo de andamento, andamento, observação do andamento da decisão.           | Híbrido (parcialmente pago para dados recentes) |
| **STJ (Portal de Dados Abertos)** | `dados.stj.jus.br`                        | CKAN API, Integração DataJud API | Metadados processuais (via integração com DataJud), dados básicos do processo, informações da Consulta Processual.                   | Gratuito           |
| **Judit.io**      | Não informado publicamente; acesso via contrato.             | API Paga (REST)            | Dados processuais completos, incluindo histórico, para avaliação de risco, compliance, crédito. Cobertura de mais de 90 tribunais.       | Pago               |
| **TRT4 (Dados Abertos)** | `dadosabertos.trt4.jus.br/api/sessoes-2grau/sessoes` | Webservice (REST)          | Dados de sessões de julgamento.                                                                                                            | Gratuito           |

### Limitações e Motivação para Uso/Não Uso

#### 1. DataJud CNJ

*   **Limitações:**
    *   Não disponibiliza o *inteiro teor* das decisões, apenas metadados e movimentações processuais.
    *   Processos que tramitam em segredo de justiça não são acessíveis.
    *   A regra de chave pública pode ser alterada pelo CNJ.
*   **Motivação para Uso:** Excelente para levantamento estatístico, acompanhamento de tendências, identificação de processos específicos e integração de informações processuais básicas em sistemas que não demandam o teor completo da jurisprudência. Cobertura nacional abrangente.
*   **Motivação para Não Uso:** Inadequado para aplicações que exigem a análise do conteúdo jurídico integral das decisões, como a construção de bases de precedentes ou elaboração de peças processuais com base em trechos específicos de votos e ementas.

#### 2. TJDFT

*   **Limitações:**
    *   Cobertura restrita à jurisprudência do TJDFT.
    *   A completude dos dados em relação ao *inteiro teor* e votos não está totalmente especificada nos resultados da busca, embora mencione "acórdãos e decisões".
*   **Motivação para Uso:** Útil para projetos focados especificamente na jurisprudência do Distrito Federal, com acesso programático facilitado e gratuito.
*   **Motivação para Não Uso:** Insuficiente para pesquisas que necessitam de abrangência nacional ou de outros tribunais específicos.

#### 3. STF (Corte Aberta)

*   **Limitações:**
    *   Acesso aos dados é via BigQuery ou download de pacotes, não sendo uma API REST tradicional para busca de jurisprudência em tempo real.
    *   Dados mais recentes podem exigir pagamento.
    *   A extração do *inteiro teor* de forma automatizada pode ser complexa e não diretamente suportada por uma API de busca.
*   **Motivação para Uso:** Valiosa para análises de alto nível da produção decisória do STF, pesquisa acadêmica e integração com ferramentas de ciência de dados.
*   **Motivação para Não Uso:** Não é a ferramenta ideal para busca individualizada e em tempo real do *inteiro teor* de acórdãos para uso direto em sistemas jurídicos transacionais sem processamento adicional.

#### 4. STJ (Portal de Dados Abertos)

*   **Limitações:**
    *   Para jurisprudência, o portal se refere à API Pública do DataJud para metadados, o que implica as mesmas limitações de não ter o *inteiro teor*.
*   **Motivação para Uso:** Acesso a metadados processuais do STJ e outros conjuntos de dados relacionados à gestão do tribunal. Útil para quem já utiliza a API do DataJud.
*   **Motivação para Não Uso:** Similar ao DataJud CNJ, não provê o *inteiro teor* da jurisprudência diretamente via API para automação.

#### 5. Judit.io

*   **Limitações:**
    *   Serviço pago.
    *   Detalhes específicos dos endpoints e formatos de dados não são publicamente disponíveis, exigindo contato comercial.
*   **Motivação para Uso:** Solução robusta para empresas e escritórios que precisam de acesso programático completo (incluindo *inteiro teor*) e em tempo real à jurisprudência de múltiplos tribunais, para fins de risco, compliance, crédito e inteligência jurídica.
*   **Motivação para Não Uso:** Não é viável para projetos com orçamento limitado ou que necessitam apenas de metadados processuais.

#### 6. TRT4 (Dados Abertos)

*   **Limitações:**
    *   Foco restrito a "Sessões de Julgamento", não sendo uma fonte abrangente para o *inteiro teor* da jurisprudência do TRT4.
*   **Motivação para Uso:** Específico para o monitoramento de pautas e resultados de sessões de julgamento do TRT4.
*   **Motivação para Não Uso:** Não atende à necessidade de busca de jurisprudência completa ou de outros tribunais.

#### Outras Fontes (JusBrasil, LexML Brasil, APIs Governamentais gerais)

*   **JusBrasil:** Não foram encontrados detalhes sobre uma API pública para acesso programático a jurisprudência. O acesso é predominantemente via interface web, e web scraping em plataformas privadas pode ter restrições legais e técnicas.
*   **LexML Brasil:** Nenhuma API para acesso programático à jurisprudência foi identificada nos resultados da pesquisa inicial.
*   **APIs Governamentais (geral):** O catálogo de APIs governamentais Gov.br foca em integração G2G e dados de transparência geral, sem oferta específica de APIs de jurisprudência em larga escala.

### Source Index

1.  Current time information in Brasilia, BR. https://www.google.com/search?q=time+in+Brasilia,+BR
2.  API Pública do DataJud - CNJ: requisição e análise com Python - YouTube. https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFsLUW4RxQvg_wRQm2mW4cc42iSXni1-kQAoeHkUP29aTEHmzvU9st9wU0VAkg8XsUfqtiJcnQxxw8XwiamWn51mScuQ1_R1oUKY4nGRZEwqxlsf2Hxe1ZsHwCfz7Xo3AtpJRcJqg==
3.  CNJ lança ferramenta pública que universaliza informações sobre processos judiciais* | Justiça Federal - 2ª Região. https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhjUAbLP1NVDRqXb_mBjqqiFl378wflZQOm2XaA6vLl5fOvNt1Wy3YYZGgR4jA-UZxbf_FyJeUKwaSudxy13JBI7ngsqZZXugvhJ_V3o4iIFhV0WEfxr0fXJmExl40H8iu8qubUpgy0zCPLGKFC52PgrCaAqAdD_TR_VsTqmGsvFwRqq5--38MOy1_E11TfsFr8YQE1CuuJE3mlUJjPHN_SPeNGpF7fR2ZdIy8UA==
4.  Pesquisa de Jurisprudência - Supremo Tribunal Federal. https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrzUlAd8VAxoCpXpIaJ1rIMFp_La83HRO7ahpRyXQLtacMeo8mTx12jraWD_AF7CgwlpmBHoXG9p-euQk5n5Wk34XCwcfkJ1E-jAzi2cK3R3ABu1-2pgRytntxpwg0b2Hj7U=
5.  STJ - Superior Tribunal de Justiça. https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGEAmDVrD-Ziy8DA1PNpmAkmTs25CZzODGImQnqcEeMfXMVVBNNBmj7h-0VKi179HxrrWV7t_qNOqywpIebeGcuJBI-KMshD9TNmkwrBv412js=
6.  Webservice ou API — Tribunal de Justiça do Distrito Federal e dos Territórios - TJDFT. https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKukQwd8kw0TgikDLHsua8EqtbWsEjw-I4wltoEJPvpXmNQbBX-kXQWRKdJAHydHQ22x_iXRDzecfNlM_rjBa6hebOiHAsom0HmOVatZwY_CV4jY8fbbarIz1MMNo37YQeJLMzIdj8heHHOntC57S_uGSmWtoMfJP-QdysFZSXrX-J_52r-SEVVPYfc1UUSqM7MTsGIIztBldjW5AJQ9G9OHolE0llpg==
7.  API Pública - DATAJUD - Portal de Dados Abertos do STJ. https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGo9Wrtp271fjArF2zSprCON8xzgHHU23Kz58SeJKiOXIiz5kRp9bOHY2pNJ6c3_zPmXlNvyfW33NH89_dfT2omF4HS9c7Zf38gQ3mQe76IjdqkN2_orvpPL5SimX9HeCDyLZxN1PJYOnUDB0mFY_HLGKc9VLfnFM6n
8.  API Pública - Portal CNJ. https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzX4YdQqSL8wa_I6VkG7VZ3aWOGXUJn1LyYaE-1t_awxHuKayrJrg5WWqRWTLJlSJGgr9C5qKmRiNhdB0jo0Fxv7ApHzpEDKii07xnkGqWFCv3TFL3KTtqmkmk-B3KQMqXOmShr5AMwiCZc6btWQ==
9.  Conjunto de dados - Portal de Dados Abertos do STJ. https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEw-FAynyCJrYC4sL54ZD42N-4yF7NOPFh2ElKWlhKspv-jU_qYzFkwfaKg5h9ZIHzGDr9zkmfAcjDvwkWFL2RHsv8HSaO_l2k0nAbSO7-Nwk80PPuwzfBq-4z1l6PKk4vzAG5KUy4=
10. Bem vindo - Portal de Dados Abertos do STJ. https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6LAKhM5yXa3ZgcFuXq0tBd4AUSsrfXtrtTPZLH6UzWU__WP316fnHqKX7GTrgSbJEhSao0Q0l1WxABJAUVB2irafnQUDGXppdYGbuSQtwUF9I6Ji7zoKDFebLRXIQ
11. Judit.io: Sua infraestrutura completa de dados Jurídicos. https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqxiGIKgZdubqLnc7Vk_mfjNZnrSDAoyNjh6RMkAYjihlnCCaOAqRIOJ9BhBdYI_h_wL5HqrO7x-skARRgNU8Gvg0UdeJAICgQJ3M=
12. Acesso a dados estatísticos e API Pública do Datajud - CNJ - TRT-2. https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYi2ok-cD5aVQBqOleuDDQcYnsHUwrecP2lxbMY0s2ICRgY8opbDFSuulkQdrPsmc8SenhlORcrCdCw8VA_Y7AWauECtGxo51RhVbdDk83_6_XyiArQC1HBiWzALvZJR2neKtiLKmMelW7LFz9k2v4mxiumF0SqVi3-sNpVNkWNoTOcLMm3-IsRqxmR8KTDiY2BDRb6dPTeBsw0zK5DS5IRNH74TYXvQolT4KGfd8qlMUgNdGjbZyuOvdJE0baEeLLo5t64cSdIw==
13. Bases Jurídico-Documentais: IGFEJ. https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUTveuePE0G3T4tXA4gvfefRvrOsgWnXSAO3dl9U5y4w95rVmmfbw5loGpcG2fZz4yeXc9Ja5VCLMR966-k74v2WsVi1IYueprip1fumU=
14. Dados Abertos - API - TRT4. https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGB8xUNOpguFiAxv85u-C3E1-quj3wZRM4v3szuDE46aVCifu2ROqzQVHEjHBNNqSaILDDu-5-4HG1N8q20BVI8YBAQjdR4Jv14zcxcZcl9LA9hquEebWSM_7wqP4N7e2AOlUrRF3kELgeXzgA==
15. Corte Aberta - Base dos Dados. https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF10JPTMieubay6NX8F2zB3pF-xj0saLw7PDjORu6fCjdFa7KNZpni1-OqHWndohWLyKlCq1oyLJIx8Z7k3fHqHi0b21vH4nv6Y16IJg6PgdfP5PbDHIvRjxFEOG-5ZDPyenhEW1ePFVOTktT0AEy5v1VxinJ6qvkqR8mYq3nX6
16. Catálogo de APIs governamentais - Portal Gov.br. https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPkhMeRBIMxewldcMFv8N_52lIdyaoTt6JpKyAMrvOQCwpVy3OUif-XioLsf_UXSApoQ2gEEr-4DDPCRVETNwUcpWyTDH1d4uQmTVo_XKH3tF4M5BfxQ3JmNZqtO18
17. DataJud: Como Consultar Processos do CNJ [Guia Completo 2024] | Blog PeríciaIA. https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFV4zvTfV06jrxF_zy5Ti69uIpzFN-gDvjbVCQG_eTcUdqshWDixBfQzIYkqDLjxu96pdzWF6RIwsSj3DYddEDjhmjepgoupZqHnBi0Ogl2_dNyrQeAA3u_buwtETrYLb-Vci8szoFVSEBkLDfTJ_XxDTKVYdDV-r7dGwkjgYKWwo7jX9oeC_xH53c=
18. Consulta Jurídica Completa em Tempo Real - Judit API. https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGp9frMh3RfTo07_5WqS_IJv4F1tHli0ZT2RnXiokmO6no5tHKHnCEnHy6MdUFAsevfFrRtu-SVRwrEZq8PApyJLskXp6ekiS0xYs2xACD-0JpEscPKqw==
19. API de Dados - Portal da Transparência do Governo Federal. https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWVkwxKS2EsXHlui8UE0oeNag6ymak1zrUgmZ9l1yrdUt58chkz2k2bXu-TudithHGDsff9wJj5dtrwePVNjtwZnqcIIf9jZjTOG0BJdb1XFoTS28bj75dvB-FowIPDjT5-rR16cUl-GIZ1g==
20. Acesso automatizado via API (Judiciário) - Dados formatos Abertos, Estruturados e Legíveis - Portal da Transparência do TJRO. https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWbu0cVLvzgBJw8lIiHTM9AH3B7KSSoqZ4qXO_HdnaDt4tQ-YMZ271bi44G-_OxNarg-MrOg_bK0ttDvtNTmFR0UYG6fCdJPTp5F-axh1IKswW2o5ioSoelNpEQB0NCTNMktzz2lCyc2nsv_K_qEdpy3O3LclaPPd8gwbsfPC_cme6Lgw9JMxK174A2TkVG03oXJhPL2aXKrKDrcZtIgtKZGE9TQ==
21. Pesquisa textual | Tribunal de Contas da União. https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH_5xSfg2n3fRNW-tVfwmuDIkytM_CJTnEvQoBqvw44iauJKKv9SeqqehvPgr4Fo8aqdlbnxUf_biStSnmWr0pkcYEEuwnjzqZeRd2x8dQBraROMa0QE3qhb7Rd
22. Easyjur Software jurídico. https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE-hHdsurxUXOOt9cMiowN4z7eCsUmQW2WEJgWSsAzrnZoiKg7HTz6a41qEYAz3hvhzOmn4LPNBAzM-9BBZhaKyk7F8AAAcvmZgoFOq2vs=
23. portal —. https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTqMbAlxzfx3YqZCJvr4WuW6ty0C2VtFjUkpP7oC_uB3GY24WKBxXFHeB3AMpXp_umsy261Q-RCfa3t0XA5Do6oKliGqEKvWmNbDJ7vifERw==
24. LDSOFT | Propriedade Intelectual no Brasil. https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFPdGwFK5vnCx5TtPJrYdfoq9IIKa0pdxPGQQArZ-2AlDpl23_y-_n3kPADXt4w2rjE-BB6H4fe9cMyD_gBUxioQiSXePo8bwdN_RHPGIz1dCBG3qk=

---

## Metadata

### Search Queries Executed

### Sources
- [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFsLUW4RxQvg_wRQm2mW4cc42iSXni1-kQAoeHkUP29aTEHmzvU9st9wU0VAkg8XsUfqtiJcnQxxw8XwiamWn51mScuQ1_R1oUKY4nGRZEwqxlsf2Hxe1ZsHwCfz7Xo3AtpJRcJqg==)
- [trf2.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFhjUAbLP1NVDRqXb_mBjqqiFl378wflZQOm2XaA6vLl5fOvNt1Wy3YYZGgR4jA-UZxbf_FyJeUKwaSudxy13JBI7ngsqZZXugvhJ_V3o4iIFhV0WEfxr0fXJmExl40H8iu8qubUpgy0zCPLGKFC52PgrCaAqAdD_TR_VsTqmGsvFwRqq5--38MOy1_E11TfsFr8YQE1CuuJE3mlUJdPHN_SPeNGpF7fR2ZdIy8UA==)
- [stj.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGo9Wrtp271fjArF2zSprCON8xzgHHU23Kz58SeJKiOXIiz5kRp9bOHY2pNJ6c3_zPmXlNvyfW33NH89_dfT2omF4HS9c7Zf38gQ3mQe76IjdqkN2_orvpPL5SimX9HeCDyLZxN1PJYOnUDB0mFY_HLGKc9VLfnFM6n)
- [cnj.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGzX4YdQqSL8wa_I6VkG7VZ3aWOGXUJn1LyYaE-1t_awxHuKayrJrg5WWqRWTLJlSJGgr9C5qKmRiNhdB0jo0Fxv7ApHzpEDKii07xnkGqWFCv3TFL3KTtqmkmk-B3KQMqXOmShr5AMwiCZc6btWQ==)
- [trt2.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYi2ok-cD5aVQBqOleuDDQcYnsHUwrecP2lxbMY0s2ICRgY8opbDFSuulkQdrPsmc8SenhlORcrCdCw8VA_Y7AWauECtGxo51RhVbdDk83_6_XyiArQC1HBiWzALvZJR2neKtiLKmMelW7LFz9k2v4mxiumF0SqVi3-sNpVNkWNoTOcLMm3-IsRqxmR8KTDiY2BDRb6dPTeBsw0zK5DS5IRNH74TYXvQolT4KGfd8qlMUgNdGjbZyuOvdJE0baEeLLo5t64cSdIw==)
- [periciaia.com.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFV4zvTfV06jrxF_zy5Ti69uIpzFN-gDvjbVCQG_eTcUdqshWDixBfQzIYkqDLjxu96pdzWF6RIwsSj3DYddEDjhmjepgoupZqHnBi0Ogl2_dNyrQeAA3u_buwtETrYLb-Vci8szoFVSEBkLDfTJ_XxDTKVYdDV-r7dGwkjgYKWwo7jX9oeC_xH53c=)
- [tjdft.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGKukQwd8kw0TgikDLHsua8EqtbWsEjw-I4wltoEJPvpXmNQbBX-kXQWRKdJAHydHQ22x_iXRDzecfNlM_rjBa6hebOiHAsom0HmOVatZwY_CV4jY8fbbarIz1MMNo37YQeJLMzIdj8heHHOntC57S_uGSmWtoMfJP-QdysFZSXrX-J_52r-SEVVPYfc1UUSqM7MTsGIIztBldjW5AJQ9G9OHolE0llpg==)
- [tjro.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWbu0cVLvzgBJw8lIiHTM9AH3B7KSSoqZ4qXO_HdnaDt4tQ-YMZ271bi44G-_OxNarg-MrOg_bK0ttDvtNTmFR0UYG6fCdJPTp5F-axh1IKswW2o5ioSoelNpEQB0NCTNMktzz2lCyc2nsv_K_qEdpy3O3LclaPPd8gwbsfPC_cme6Lgw9JMxK174A2TkVG03oXJhPL2aXKrKDrcZtIgtKZGE9TQ==)
- [stf.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGrzUlAd8VAxoCpXpIaJ1rIMFp_La83HRO7ahpRyXQLtacMeo8mTxz12jraWD_AF7CgwlpmBHoXG9p-euQk5n5Wk34XCwcfkJ1E-jAzi2cK3R3ABu1-2pgRytntxpwg0b2Hj7U=)
- [basedosdados.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF10JPTMieubay6NX8F2zB3pF-xj0saLw7PDjORu6fCjdFa7KNZpni1-OqHWndohWLsKlCq1oyLJIx8Z7k3fHqHi0b21vH4nv6Y16IJg6PgdfP5PbDHIvRjxFEOG-5ZDPyenhEW1ePFVOTktT0AEy5v1VxinJ6qvkqR8mYq3nX6)
- [judit.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFqxiGIKgZdubqLnc7Vk_mfjNZnrSDAoyNjh6RMkAYjihlnCCaOAqRIOJ9BhBdYI_h_wL5HqrO7x-skARRgNU8Gvg0UdeJAICgQJ3M=)
- [judit.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGp9frMh3RfTo07_5WqS_IJv4F1tHli0ZT2RnXiokmO6no5tHKHnCEnHy6MdUFAsevfFrRtu-SVRwrEZq8PApyJLskXp6ekiS0xYs2xACD-0JpEscPKqw==)
- [stj.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEw-FAynyCJrYC4sL54ZD42N-4yF7NOPFh2ElKWlhKspv-jU_qYzFkwfaKg5h9ZIHzGDr9zkmfAcjDvwkWFL2RHsv8HSaO_l2k0nAbSO7-Nwk80PPuwzfBq-4z1l6PKk4vzAG5KUy4=)
- [stj.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF6LAKhM5yXa3ZgcFuXq0tBd4AUSsrfXtrtTPZLH6UzWU__WP316fnHqKX7GTrgSbJEhSao0Q0l1WxABJAUVB2irafnQUDGXppdYGbuSQtwUF9I6Ji7zoKDFebLRXIQ)
- [trt4.jus.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGB8xUNOpguFiAxv85u-C3E1-quj3wZRM4v3szuDE46aVCifu2ROqzQVHEjHBNNqSaILDDu-5-4HG1N8q20BVI8YBAQjdR4Jv14zcxcZcl9LA9hquEebWSM_7wqP4N7e2AOlUrRF3kELgeXzgA=)
- [www.gov.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPkhMeRBIMxewldcMFv8N_52lIdyaoTt6JpKyAMrvOQCwpVy3OUif-XioLsf_UXSApoQ2gEEr-4DDPCRVETNwUcpWyTDH1d4uQmTVo_XKH3tF4M5BfxQ3JmNZqtO18)
- [portaldatransparencia.gov.br](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHWVkwxKS2EsXHlui8UE0oeNag6ymak1zrUgmZ9l1yrdUt58chkz2k2bXu-TudithHGDsff9wJj5dtrwePVNjtwZnqcIIf9jZjTOG0BJdb1XFoTS28bj75dvB-FowIPDjT5-rR16cUl-GIZ1g==)
