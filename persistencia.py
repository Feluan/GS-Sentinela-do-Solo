import json
CHAVES_OBRIGATORIAS = ('clusters', 'estacas', 'relatos', 'abrigos', 'taludes', 'historico')

def _converter_coordenadas(dados):
    for lista in ('clusters', 'abrigos', 'relatos'):
        for item in dados[lista]:
            if 'coordenadas' in item and item['coordenadas'] is not None:
                item['coordenadas'] = tuple(item['coordenadas'])

def carregar_dados(caminho):
    try:
        with open(caminho, 'r', encoding='utf-8') as arquivo:
            dados = json.load(arquivo)
        for chave in CHAVES_OBRIGATORIAS:
            if chave not in dados:
                raise ValueError(f"chave '{chave}' ausente no arquivo")
        _converter_coordenadas(dados)
        return dados
    except FileNotFoundError:
        print(f"Erro: o arquivo '{caminho}' não foi encontrado.")
    except json.JSONDecodeError:
        print(f"Erro: o arquivo '{caminho}' está mal formatado (JSON inválido).")
    except ValueError as erro:
        print(f'Erro nos dados: {erro}.')
    except OSError:
        print(f"Erro: não foi possível abrir '{caminho}'.")
    return None

def salvar_dados(caminho, dados):
    try:
        with open(caminho, 'w', encoding='utf-8') as arquivo:
            json.dump(dados, arquivo, indent=2, ensure_ascii=False)
        return True
    except (OSError, TypeError, ValueError):
        return False
