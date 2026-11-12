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

def mostrar_status(dados, cluster):
    titulo(f"STATUS - {cluster['nome']}")
    print(f"  Solo: {cluster['solo']} | Famílias no cluster: {cluster['familias']}")
    mostrar_banner(cluster)
    rotulo = descrever_estado(cluster)[0]
    if rotulo == 'AMARELO':
        print('  Checklist de preparação:')
        for item in CHECKLIST_AMARELO:
            print(f'   [ ] {item}')
    elif rotulo == 'VERMELHO' and cluster['evacuacao_autorizada']:
        coordenada = cluster['coordenadas']
        abrigo, km = buscar_abrigo_proximo(coordenada, dados['abrigos'], cluster['id'])
        if abrigo is not None:
            print(f"  Abrigo: {abrigo['nome']} - {int(km * 1000)} m, cerca de {minutos_a_pe(km)} min a pé.")
        print('  Leve apenas o essencial.')
    print('  Dados da Defesa Civil e da estaca inteligente da sua região.')

def enviar_relato(dados, cluster, nome):
    titulo('NOVO RELATO')
    for numero, tipo in TIPOS_RELATO.items():
        print(f'  {numero} - {tipo}')
    tipo = TIPOS_RELATO[ler_inteiro('Tipo de relato: ', 1, len(TIPOS_RELATO))]
    descricao = ler_texto('Descreva o que você viu: ')
    foto = ler_texto('Nome ou descrição da foto (Enter para pular): ', obrigatorio=False)
    coordenada = ler_coordenada('Localização (digite as coordenadas do local):')
    relato = {'id': proximo_id(dados['relatos']), 'cluster_id': cluster['id'], 'autor': nome, 'tipo': tipo, 'descricao': descricao, 'foto': foto, 'coordenadas': coordenada, 'status': 'Em Vistoria'}
    dados['relatos'].append(relato)
    reavaliar_por_id(dados, cluster['id'])
    salvar(dados)
    print(f"Relato #{relato['id']} enviado. Obrigado por ajudar a proteger sua rua!")

def relatos_do_morador(dados, cluster, nome):
    meus = []
    for relato in dados['relatos']:
        if relato['cluster_id'] == cluster['id'] and relato['autor'].lower() == nome.lower():
            meus.append(relato)
            print(f"  #{relato['id']} [{relato['status']}] {relato['tipo']} - {relato['descricao']}")
    if not meus:
        print('  Você ainda não enviou relatos neste cluster.')
    return meus

def editar_relato(dados, cluster, nome):
    titulo('EDITAR MEU RELATO')
    meus = relatos_do_morador(dados, cluster, nome)
    if not meus:
        return
    relato = buscar_por_id(meus, ler_inteiro('Número do relato: ', 1, 9999))
    if relato is None:
        print('Relato não encontrado entre os seus.')
        return
    nova = ler_texto('Nova descrição (Enter para manter): ', obrigatorio=False)
    if nova != '':
        relato['descricao'] = nova
    if ler_confirmacao('Deseja trocar o tipo do relato?'):
        for numero, tipo in TIPOS_RELATO.items():
            print(f'  {numero} - {tipo}')
        relato['tipo'] = TIPOS_RELATO[ler_inteiro('Novo tipo: ', 1, len(TIPOS_RELATO))]
    relato['status'] = 'Em Vistoria'
    salvar(dados)
    print('Relato atualizado.')