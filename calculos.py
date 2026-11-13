TAXA_MARGEM = 0.4
CHUVA_SATURACAO = 80.0
TOLERANCIA_ESTAVEL = 0.05
PONTOS_CONFIRMADO = 10
PONTOS_EM_VISTORIA = 5
SCORE_ELEVA_CLUSTER = 20
PONTOS_POR_ESTADO = {1: 0, 2: 20, 3: 40}
VELOCIDADE_A_PE_KM_H = 5.0

def calcular_derivada(theta_ant, theta_atual, delta_t):
    if delta_t <= 0:
        raise ValueError('O intervalo de tempo deve ser maior que zero.')
    return (theta_atual - theta_ant) / delta_t

def classificar_estado(taxa, taxa_critica, chuva_mm):
    velocidade = abs(taxa)
    if velocidade >= taxa_critica:
        return 3
    elif velocidade >= TAXA_MARGEM * taxa_critica:
        return 2
    elif chuva_mm >= CHUVA_SATURACAO:
        return 2
    else:
        return 1

def calcular_score_crowd(cluster_id, relatos):
    pontos = 0
    for relato in relatos:
        if relato['cluster_id'] == cluster_id:
            if relato['status'] == 'Confirmado':
                pontos += PONTOS_CONFIRMADO
            elif relato['status'] == 'Em Vistoria':
                pontos += PONTOS_EM_VISTORIA
    return pontos

def calcular_score(estado_estaca, score_crowd):
    return min(100, PONTOS_POR_ESTADO.get(estado_estaca, 0) + score_crowd)

def estado_estaca(estaca, cluster):
    return classificar_estado(estaca['taxa'], cluster['taxa_critica'], estaca['chuva_mm'])

def reavaliar_cluster(cluster, estaca, relatos):
    cluster['score_crowd'] = calcular_score_crowd(cluster['id'], relatos)
    estado = estado_estaca(estaca, cluster)
    if estado == 1 and cluster['score_crowd'] >= SCORE_ELEVA_CLUSTER:
        estado = 2
    cluster['estado'] = estado
    if estado >= 2:
        cluster['retorno_seguro'] = False
    return estado

def calcular_distancia_km(a, b):
    # Esta distância é aproximada e serve apenas para comparar os abrigos.
    dlat = a[0] - b[0]
    dlon = a[1] - b[1]
    return (dlat ** 2 + dlon ** 2) ** 0.5 * 111.0

def buscar_abrigo_proximo(coordenada, abrigos, cluster_id=None):
    melhor = None
    menor = None
    for abrigo in abrigos:
        if cluster_id is not None and abrigo['cluster_id'] not in (cluster_id, None):
            continue
        distancia = calcular_distancia_km(coordenada, abrigo['coordenadas'])
        if menor is None or distancia < menor:
            melhor = abrigo
            menor = distancia
    return (melhor, menor)

def minutos_a_pe(distancia_km):
    minutos = distancia_km / VELOCIDADE_A_PE_KM_H * 60
    return int(minutos) + (1 if minutos > int(minutos) else 0)

def buscar_por_id(lista, id_procurado):
    for item in lista:
        if item['id'] == id_procurado:
            return item
    return None

def proximo_id(lista):
    maior = 0
    for item in lista:
        if item['id'] > maior:
            maior = item['id']
    return maior + 1
