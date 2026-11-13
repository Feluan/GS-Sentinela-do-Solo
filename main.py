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

def excluir_relato(dados, cluster, nome):
    titulo('EXCLUIR MEU RELATO')
    meus = relatos_do_morador(dados, cluster, nome)
    if not meus:
        return
    relato = buscar_por_id(meus, ler_inteiro('Número do relato: ', 1, 9999))
    if relato is None:
        print('Relato não encontrado entre os seus.')
    elif ler_confirmacao(f"Excluir o relato #{relato['id']}?"):
        dados['relatos'].remove(relato)
        reavaliar_por_id(dados, cluster['id'])
        salvar(dados)
        print('Relato excluído.')
    else:
        print('Nada foi excluído.')

def consultar_abrigo(dados, cluster):
    titulo('ABRIGO MAIS PRÓXIMO')
    coordenada = ler_coordenada('Sua localização (digite as coordenadas):')
    abrigo, km = buscar_abrigo_proximo(coordenada, dados['abrigos'], cluster['id'])
    if abrigo is None:
        print('Nenhum abrigo cadastrado para sua região.')
        return
    print(f"  Abrigo: {abrigo['nome']}")
    print(f'  Distância: {int(km * 1000)} m | Tempo a pé: cerca de {minutos_a_pe(km)} min')
    print(f"  Local do abrigo: {abrigo['coordenadas']}")
    if not cluster['evacuacao_autorizada']:
        print('  (Consulta informativa: não há evacuação autorizada agora.)')

def menu_cidadao(dados):
    titulo('PERFIL CIDADÃO')
    nome = ler_texto('Seu nome: ')
    print('Em qual cluster você mora?')
    cluster = escolher_por_id(dados['clusters'], 'cluster')
    while True:
        titulo(f"CIDADÃO: {nome} | {cluster['nome']}")
        print('1 - Ver status do meu cluster\n2 - Enviar relato\n3 - Listar relatos do cluster')
        print('4 - Editar meu relato\n5 - Excluir meu relato\n6 - Achar abrigo mais próximo\n0 - Voltar')
        match ler_inteiro('Escolha: ', 0, 6):
            case 1:
                mostrar_status(dados, cluster)
            case 2:
                enviar_relato(dados, cluster, nome)
            case 3:
                titulo('RELATOS DO CLUSTER')
                listar_relatos_cluster(dados, cluster['id'])
            case 4:
                editar_relato(dados, cluster, nome)
            case 5:
                excluir_relato(dados, cluster, nome)
            case 6:
                consultar_abrigo(dados, cluster)
            case 0:
                return

def simular_leitura(dados):
    titulo('SIMULAR LEITURA DA ESTACA')
    estaca = escolher_por_id([{'id': e['id'], 'nome': f"Estaca {e['id']} (cluster {e['cluster_id']})"} for e in dados['estacas']], 'estaca')
    estaca = buscar_por_id(dados['estacas'], estaca['id'])
    cluster = buscar_por_id(dados['clusters'], estaca['cluster_id'])
    theta_novo = ler_float('Novo ângulo θ (graus, 0 a 90): ', 0, 90)
    intervalo = ler_float('Horas desde a leitura anterior (0,01 a 72): ', 0.01, 72)
    chuva = ler_float('Chuva acumulada nas últimas 24 h (mm): ', 0, 500)
    try:
        taxa = calcular_derivada(estaca['theta_atual'], theta_novo, intervalo)
    except ValueError as erro:
        print(f'Leitura descartada: {erro}')
        return
    estaca['theta_anterior'] = estaca['theta_atual']
    estaca['theta_atual'] = theta_novo
    estaca['intervalo_h'] = intervalo
    estaca['chuva_mm'] = chuva
    estaca['taxa'] = taxa
    estado = reavaliar_cluster(cluster, estaca, dados['relatos'])
    registrar_evento(dados, f"Leitura da estaca {estaca['id']}: {taxa:.2f} °/h", 'Defesa Civil', estado)
    salvar(dados)
    print(f"dθ/dt = {taxa:.2f} °/h ({taxa / cluster['taxa_critica'] * 100:.0f}% da taxa crítica)")
    print(f"Cluster {cluster['nome']}: estado {NOMES_ESTADO[estado]}")
    if estado == 3 and (not cluster['evacuacao_autorizada']):
        print('>>> ALERTA SUGERIDO: avalie e decida sobre a evacuação preventiva.')
    elif estado == 2:
        print(f'>>> Margem pessimista de {int(TAXA_MARGEM * 100)}% ou solo saturado: alerta amarelo.')

def ver_clusters(dados):
    titulo('CLUSTERS')
    for cluster in dados['clusters']:
        estaca = buscar_estaca_do_cluster(dados, cluster['id'])
        score = calcular_score(estado_estaca(estaca, cluster), cluster['score_crowd'])
        rotulo = descrever_estado(cluster)[0]
        print(f"  {cluster['id']} - {cluster['nome']} ({cluster['solo']})")
        print(f"      estado: [{rotulo}] | score de risco: {score}/100 | taxa: {estaca['taxa']:.2f} °/h | chuva: {estaca['chuva_mm']:.0f} mm")
        if cluster['estado'] == 3 and (not cluster['evacuacao_autorizada']):
            print('      >>> ALERTA SUGERIDO: aguardando decisão do agente.')
        separador()

def buscar_estaca_do_cluster(dados, cluster_id):
    for estaca in dados['estacas']:
        if estaca['cluster_id'] == cluster_id:
            return estaca
    return None

def avaliar_alerta(dados, cluster):
    estaca = buscar_estaca_do_cluster(dados, cluster['id'])
    pct = abs(estaca['taxa']) / cluster['taxa_critica'] * 100
    titulo(f"AVALIAÇÃO - {cluster['nome']}")
    print(f"  Sensor : θ = {estaca['theta_atual']:.1f}° | dθ/dt = {estaca['taxa']:.2f} °/h ({pct:.0f}% da taxa crítica de {cluster['taxa_critica']} °/h)")
    print(f"  Clima  : {estaca['chuva_mm']:.0f} mm em 24 h")
    print(f"  Relatos: score dos moradores = {cluster['score_crowd']}")
    listar_relatos_cluster(dados, cluster['id'])
    print(f"  Estado calculado: {NOMES_ESTADO[cluster['estado']]}")
    return pct

def triar_relatos(dados):
    titulo('TRIAGEM DE RELATOS')
    if not dados['relatos']:
        print('Não há relatos para triar.')
        return
    for relato in dados['relatos']:
        print(f"  #{relato['id']} [{relato['status']}] cluster {relato['cluster_id']} - {relato['tipo']}: {relato['descricao']} | foto: {relato['foto'] or '-'}")
    relato = buscar_por_id(dados['relatos'], ler_inteiro('Número do relato: ', 1, 9999))
    if relato is None:
        print('Relato não encontrado.')
        return
    for numero, status in STATUS_RELATO.items():
        print(f'  {numero} - {status}')
    relato['status'] = STATUS_RELATO[ler_inteiro('Novo status: ', 1, 3)]
    reavaliar_por_id(dados, relato['cluster_id'])
    registrar_evento(dados, f"Relato #{relato['id']} marcado como {relato['status']}", 'Defesa Civil', buscar_por_id(dados['clusters'], relato['cluster_id'])['estado'])
    salvar(dados)
    print('Status atualizado.')

def autorizar_evacuacao(dados):
    titulo('AUTORIZAR EVACUAÇÃO PREVENTIVA')
    cluster = escolher_por_id(dados['clusters'], 'cluster')
    avaliar_alerta(dados, cluster)
    if cluster['evacuacao_autorizada']:
        print('A evacuação já está autorizada para este cluster.')
    elif cluster['estado'] != 3:
        print('Bloqueado: a evacuação só pode ser autorizada com estado VERMELHO.')
    elif ler_confirmacao('1ª confirmação: você analisou sensor, clima e relatos?') and ler_confirmacao('2ª confirmação: AUTORIZAR a evacuação preventiva (responsabilidade pública)?'):
        cluster['evacuacao_autorizada'] = True
        cluster['retorno_seguro'] = False
        cluster['vistoria_registrada'] = False
        registrar_evento(dados, 'Evacuação preventiva autorizada', 'Defesa Civil', cluster['estado'])
        salvar(dados)
        print('Evacuação autorizada. Moradores serão avisados com a rota até o abrigo.')
    else:
        print('Evacuação NÃO autorizada.')

def registrar_vistoria(dados):
    titulo('REGISTRAR VISTORIA')
    cluster = escolher_por_id(dados['clusters'], 'cluster')
    if not cluster['evacuacao_autorizada']:
        print('Este cluster não está em evacuação; não há vistoria de retorno a registrar.')
    elif ler_confirmacao('Confirma que a vistoria presencial foi concluída?'):
        cluster['vistoria_registrada'] = True
        registrar_evento(dados, 'Vistoria registrada', 'Defesa Civil', cluster['estado'])
        salvar(dados)
        print('Vistoria registrada.')

def liberar_retorno(dados):
    titulo('LIBERAR RETORNO SEGURO')
    cluster = escolher_por_id(dados['clusters'], 'cluster')
    estaca = buscar_estaca_do_cluster(dados, cluster['id'])
    if not cluster['evacuacao_autorizada']:
        print('Bloqueado: este cluster não está em evacuação.')
    elif abs(estaca['taxa']) > TOLERANCIA_ESTAVEL:
        print(f"Bloqueado: a encosta ainda se move (dθ/dt = {estaca['taxa']:.2f} °/h).")
        print('O retorno só é liberado quando dθ/dt chega a zero.')
    elif not cluster['vistoria_registrada']:
        print('Bloqueado: registre a vistoria antes de liberar o retorno.')
    elif ler_confirmacao('Confirma o retorno seguro das famílias?'):
        cluster['retorno_seguro'] = True
        cluster['evacuacao_autorizada'] = False
        cluster['vistoria_registrada'] = False
        reavaliar_por_id(dados, cluster['id'])
        cluster['retorno_seguro'] = True
        registrar_evento(dados, 'Retorno seguro liberado', 'Defesa Civil', cluster['estado'])
        salvar(dados)
        print('Retorno seguro liberado. As famílias serão avisadas.')

def menu_defesa(dados):
    while True:
        titulo('PERFIL DEFESA CIVIL')
        print('1 - Simular leitura da estaca\n2 - Ver clusters em risco\n3 - Avaliar alerta')
        print('4 - Triar relatos\n5 - Autorizar evacuação preventiva\n6 - Registrar vistoria')
        print('7 - Liberar retorno seguro\n8 - Ver histórico de alertas\n0 - Voltar')
        match ler_inteiro('Escolha: ', 0, 8):
            case 1:
                simular_leitura(dados)
            case 2:
                ver_clusters(dados)
            case 3:
                avaliar_alerta(dados, escolher_por_id(dados['clusters'], 'cluster'))
            case 4:
                triar_relatos(dados)
            case 5:
                autorizar_evacuacao(dados)
            case 6:
                registrar_vistoria(dados)
            case 7:
                liberar_retorno(dados)
            case 8:
                titulo('HISTÓRICO')
                for evento in dados['historico']:
                    print(f"  {evento['data']} | {evento['perfil']} | {evento['acao']} | estado {NOMES_ESTADO[evento['estado']]}")
                if not dados['historico']:
                    print('  Nenhum evento registrado.')
            case 0:
                return

def listar_empresas(taludes):
    empresas = []
    for talude in taludes:
        if talude['empresa'] not in empresas:
            empresas.append(talude['empresa'])
    return empresas

def taludes_da_empresa(dados, empresa):
    return [t for t in dados['taludes'] if t['empresa'] == empresa]

def ver_taludes(dados, empresa):
    titulo(f'TALUDES - {empresa}')
    for talude in taludes_da_empresa(dados, empresa):
        cluster = buscar_por_id(dados['clusters'], talude['cluster_id'])
        print(f"  {talude['id']} - {talude['nome']}")
        print(f"      estado: [{NOMES_ESTADO[cluster['estado']]}] | circulação: {talude['circulacao']}")

def alterar_circulacao(dados, empresa, novo_valor):
    ver_taludes(dados, empresa)
    talude = buscar_por_id(taludes_da_empresa(dados, empresa), ler_inteiro('Número do talude: ', 1, 9999))
    if talude is None:
        print('Talude não encontrado entre os da sua empresa.')
    elif talude['circulacao'] == novo_valor:
        print(f"A circulação já está '{novo_valor}'.")
    elif ler_confirmacao(f"Confirma mudar a circulação de '{talude['nome']}' para {novo_valor}?"):
        talude['circulacao'] = novo_valor
        cluster = buscar_por_id(dados['clusters'], talude['cluster_id'])
        registrar_evento(dados, f"Circulação {novo_valor}: {talude['nome']}", empresa, cluster['estado'])
        salvar(dados)
        print('Circulação atualizada. Esta ação não aciona alerta público.')

def relatorio_familias(dados, empresa):
    titulo(f'FAMÍLIAS PROTEGIDAS - {empresa}')
    vistos = []
    protegidas = 0
    em_alerta = 0
    for talude in taludes_da_empresa(dados, empresa):
        if talude['cluster_id'] not in vistos:
            vistos.append(talude['cluster_id'])
            cluster = buscar_por_id(dados['clusters'], talude['cluster_id'])
            protegidas += cluster['familias']
            if cluster['estado'] >= 2:
                em_alerta += cluster['familias']
    print(f'  Clusters monitorados: {len(vistos)}')
    print(f'  Famílias protegidas pelos seus sensores: {protegidas}')
    print(f'  Famílias em cluster com alerta ativo: {em_alerta}')
    print('  Selo: Parceiro ESG Sentinela do Solo')

def menu_empresa(dados):
    titulo('PERFIL EMPRESA')
    empresas = listar_empresas(dados['taludes'])
    for numero, nome in enumerate(empresas, start=1):
        print(f'  {numero} - {nome}')
    empresa = empresas[ler_inteiro('Sua empresa: ', 1, len(empresas)) - 1]
    while True:
        titulo(f'EMPRESA: {empresa}')
        print('1 - Ver taludes monitorados\n2 - Paralisar circulação\n3 - Retomar circulação')
        print('4 - Relatório de famílias protegidas\n0 - Voltar')
        match ler_inteiro('Escolha: ', 0, 4):
            case 1:
                ver_taludes(dados, empresa)
            case 2:
                alterar_circulacao(dados, empresa, 'paralisada')
            case 3:
                alterar_circulacao(dados, empresa, 'normal')
            case 4:
                relatorio_familias(dados, empresa)
            case 0:
                return

def main():
    dados = carregar_dados(CAMINHO_DADOS)
    if dados is None:
        print('Não foi possível iniciar o sistema.')
        return
    while True:
        titulo('SENTINELA DO SOLO')
        print('1 - Cidadão\n2 - Defesa Civil\n3 - Empresa\n0 - Sair')
        match ler_inteiro('Escolha seu perfil: ', 0, 3):
            case 1:
                menu_cidadao(dados)
            case 2:
                menu_defesa(dados)
            case 3:
                menu_empresa(dados)
            case 0:
                print('Até logo. Cuide-se e fique atento ao seu cluster.')
                break
if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print('\nPrograma encerrado.')
