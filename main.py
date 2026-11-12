from datetime import datetime
from calculos import TAXA_MARGEM, TOLERANCIA_ESTAVEL, calcular_derivada, calcular_score, reavaliar_cluster, estado_estaca, buscar_abrigo_proximo, minutos_a_pe, buscar_por_id, proximo_id
from persistencia import carregar_dados, salvar_dados
from validacao import ler_inteiro, ler_float, ler_texto, ler_confirmacao, ler_coordenada
CAMINHO_DADOS = 'dados.json'
NOMES_ESTADO = {0: 'ERRO DE LEITURA', 1: 'VERDE', 2: 'AMARELO', 3: 'VERMELHO'}
TIPOS_RELATO = {1: 'rachadura', 2: "mina d'água", 3: 'árvore inclinada', 4: 'poste inclinado'}
STATUS_RELATO = {1: 'Em Vistoria', 2: 'Confirmado', 3: 'Descartado'}
CHECKLIST_AMARELO = ('Guardar documentos em sacos plásticos', 'Separar remédios e itens de primeiros socorros', 'Preparar os pets (coleira, ração, água)', 'Carregar o celular e deixar uma lanterna à mão', 'Combinar com a família um ponto de encontro')

def titulo(texto):
    print('\n' + '=' * 52)
    print(texto.center(52))
    print('=' * 52)

def separador():
    print('-' * 52)

def salvar(dados):
    if not salvar_dados(CAMINHO_DADOS, dados):
        print('Atenção: não foi possível salvar os dados no arquivo.')

def registrar_evento(dados, acao, perfil, estado):
    dados['historico'].append({'data': datetime.now().strftime('%d/%m/%Y %H:%M'), 'acao': acao, 'perfil': perfil, 'estado': estado})

def escolher_por_id(lista, rotulo):
    while True:
        for item in lista:
            print(f"  {item['id']} - {item['nome']}")
        item = buscar_por_id(lista, ler_inteiro(f'Escolha o {rotulo} (número): ', 1, 9999))
        if item is not None:
            return item
        print('Número não encontrado. Tente novamente.')

def descrever_estado(cluster):
    if cluster['retorno_seguro']:
        return ('RETORNO SEGURO', 'Vistoria concluída: você já pode voltar para casa.')
    if cluster['evacuacao_autorizada']:
        return ('VERMELHO', 'Evacuação preventiva autorizada. Siga a rota até o abrigo.')
    estado = cluster['estado']
    if estado == 3:
        return ('VERMELHO', 'Risco alto. A Defesa Civil está avaliando. Mantenha a calma.')
    if estado == 2:
        return ('AMARELO', 'Solo úmido: prepare-se com calma.')
    if estado == 1:
        return ('VERDE', 'Solo firme na sua região.')
    return ('SEM LEITURA', 'Estamos verificando o sensor. Nenhuma ação necessária agora.')

def mostrar_banner(cluster):
    rotulo, mensagem = descrever_estado(cluster)
    separador()
    print(f'  ESTADO: [{rotulo}]')
    print(f'  {mensagem}')
    separador()

def listar_relatos_cluster(dados, cluster_id):
    total = 0
    for relato in dados['relatos']:
        if relato['cluster_id'] == cluster_id:
            total += 1
            print(f"  #{relato['id']} [{relato['status']}] {relato['tipo']} - {relato['descricao']} (por {relato['autor']})")
    if total == 0:
        print('  Nenhum relato neste cluster.')
    return total

def reavaliar_por_id(dados, cluster_id):
    cluster = buscar_por_id(dados['clusters'], cluster_id)
    for estaca in dados['estacas']:
        if estaca['cluster_id'] == cluster_id:
            reavaliar_cluster(cluster, estaca, dados['relatos'])

