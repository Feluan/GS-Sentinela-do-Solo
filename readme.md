# Sentinela do Solo – Computational Thinking with Python

**Integrantes:** 
Caio Maluzza: 572906
Felipe Luan: 569565
Rafaella: 572296
Pedro Alves: 569192
Anderson Marcollino: 574066

## Problema
Na região metropolitana de São Paulo, tempestades causam deslizamentos mortais. A Defesa Civil não
consegue vigiar cada encosta e, quando o risco é detectado, o aviso ao morador falha (pânico ou atraso).
O **Sentinela do Solo** usa poucas "estacas inteligentes" (sensor de inclinação), cruza a inclinação com a
chuva, estende o risco a ruas do mesmo tipo de solo (cluster) e usa relatos dos moradores. **Quem decide evacuar é sempre
um agente da Defesa Civil.** ODS 11 e 13.

Este programa é a versão em terminal (simulada) do sistema.

## Como rodar
Requisito: Python 3.10 ou superior (usa `match/case`).

```
python main.py
```
Mantenha `dados.json` na mesma pasta dos arquivos `.py`. Para restaurar os dados de exemplo, use a cópia original do ZIP.

## Arquivos
| Arquivo | Função |
|---|---|
| `main.py` | Menu principal (`while` + `match/case`) e os três perfis |
| `calculos.py` | Derivada, classificação do estado, score de risco, abrigo mais próximo |
| `validacao.py` | Leitura e validação de entradas (`try/except`) |
| `persistencia.py` | Leitura e gravação do JSON (`try/except`) |
| `dados.json` | Clusters, estacas, relatos, abrigos, taludes e histórico |

## Funcionalidades
**Cidadão:** ver status do cluster (verde, amarelo com checklist, vermelho com abrigo, retorno seguro), enviar,
listar, editar e excluir relatos (rachadura, mina d'água, árvore ou poste inclinado) e achar o abrigo mais próximo.

**Defesa Civil:** simular leitura da estaca, ver clusters em risco, avaliar alerta, triar relatos
(Em Vistoria, Confirmado, Descartado), autorizar evacuação (confirmação dupla), registrar vistoria,
liberar retorno seguro e ver histórico.

**Empresa:** ver taludes monitorados, paralisar/retomar circulação (só da própria empresa) e relatório de famílias protegidas.

## Regras e cálculos (mesmos valores das outras disciplinas)
- `dθ/dt = (θ_atual − θ_anterior) / Δt` em °/h.
- Taxa crítica: 2,0 °/h (Argissolo e Latossolo) e 1,5 °/h (Aterro Antrópico).
- Verde: abaixo de 40% da taxa crítica · Amarelo: de 40% a 100% (ou chuva ≥ 80 mm/24 h) · Vermelho: 100% ou mais.
- Relatos pontuam o cluster (confirmado = 10, em vistoria = 5); score ≥ 20 eleva verde para amarelo.
- Evacuação: só com estado vermelho e dupla confirmação (RN01).
- Retorno seguro: só com evacuação autorizada, vistoria registrada e dθ/dt ≈ 0 (tolerância de 0,05 °/h) (RN03).

## Adaptações por causa da disciplina
- Câmera: a foto é um campo de texto (nome/descrição). GPS: coordenadas digitadas. Mapa e câmera reais ficam no React.
- Chuva: simulada por digitação (sem API de clima).
- Os clusters, abrigos e empresas do `dados.json` são **exemplos fictícios**.
