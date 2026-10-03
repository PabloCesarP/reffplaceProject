"""
Lógica de cálculo, portada 1:1 das fórmulas da planilha "megabraincssbuy.xlsx".

Este módulo não importa Flask nem SQLAlchemy de propósito: recebe números
(ou objetos simples com atributos), devolve números. Isso permite testar
sem subir servidor e reutilizar em qualquer outro contexto (API, script, etc).

Correspondência com a planilha:
    B4  -> peso_primario
    B5  -> peso_secundario
    B6  -> seguro_pct
    B7  -> taxa_servico_pct
    B8  -> cotacao
    B11 -> peso_total (SUM dos pesos dos produtos)
    B12 -> frete_internacional_total()
    Colunas B..J de cada produto -> calcular_produto()

Nota: a célula J15 da planilha original usa divisão (`=I15/$B$8`) enquanto
J16:J34 usam multiplicação (`=I16*$B$8`). O texto da própria planilha (linha
45) descreve a regra como multiplicação, então é isso que este módulo usa.
Vale corrigir a célula J15 na planilha também.
"""

import math


def frete_internacional_total(peso_total_g, peso_primario, peso_secundario):
    """
    Frete Internacional Total (¥) = Peso Primário (cobre até 1kg do pedido
    todo) + Peso Secundário x kg adicionais do peso total (arredondado
    para cima). Ex.: peso total 2100g, primário 20¥, secundário 50¥
    -> 20 + 2x50 = 120¥.
    """
    if peso_total_g <= 1000:
        return peso_primario
    kg_extra = math.ceil((peso_total_g - 1000) / 1000)
    return peso_primario + kg_extra * peso_secundario


def calcular_produto(preco, frete_interno, peso_g, peso_total_g,
                      frete_intl_total, seguro_pct, taxa_servico_pct, cotacao):
    """
    Calcula todas as colunas derivadas (E..J) para um único produto.

    - Frete Internacional (¥): fatia do frete total proporcional ao peso do item.
    - Seguro (¥) = seguro_pct x (Preço + Frete Interno + Frete Internacional).
    - Subtotal (¥) = Preço + Frete Interno + Frete Internacional + Seguro.
    - Taxa de Serviço (¥) = taxa_servico_pct x Subtotal.
    - Total (¥) = Subtotal + Taxa de Serviço.
    - Total (R$) = Total (¥) / Cotação.
    """
    frete_intl = round((peso_g / peso_total_g) * frete_intl_total, 2) if peso_total_g else 0.0
    seguro = (preco + frete_interno + frete_intl) * seguro_pct
    subtotal = preco + frete_interno + frete_intl + seguro
    taxa_servico = subtotal * taxa_servico_pct
    total_yuan = subtotal + taxa_servico
    total_reais = total_yuan / cotacao

    return {
        "frete_intl": frete_intl,
        "seguro": seguro,
        "subtotal": subtotal,
        "taxa_servico": taxa_servico,
        "total_yuan": total_yuan,
        "total_reais": total_reais,
    }


def calcular_pedido(pedido):
    """
    Recebe um objeto `pedido` com os atributos:
        peso_primario, peso_secundario, seguro_pct, taxa_servico_pct, cotacao
    e uma coleção `pedido.produtos` de objetos com:
        preco, frete_interno, peso_g

    Retorna (linhas, totais):
        linhas: lista de dicts, um por produto, com o produto original em
                "produto" e os campos calculados ao lado (equivalente a uma
                linha da tabela da planilha).
        totais: dict com a linha "TOTAL" da planilha (somatório de tudo).
    """
    produtos = list(pedido.produtos)
    peso_total = sum(p.peso_g or 0 for p in produtos)
    frete_intl_total = frete_internacional_total(
        peso_total, pedido.peso_primario, pedido.peso_secundario
    )

    linhas = []
    for p in produtos:
        calc = calcular_produto(
            preco=p.preco or 0,
            frete_interno=p.frete_interno or 0,
            peso_g=p.peso_g or 0,
            peso_total_g=peso_total,
            frete_intl_total=frete_intl_total,
            seguro_pct=pedido.seguro_pct,
            taxa_servico_pct=pedido.taxa_servico_pct,
            cotacao=pedido.cotacao,
        )
        linhas.append({"produto": p, **calc})

    totais = {
        "peso_total": peso_total,
        "frete_intl_total": frete_intl_total,
        "preco": sum(l["produto"].preco or 0 for l in linhas),
        "frete_interno": sum(l["produto"].frete_interno or 0 for l in linhas),
        "frete_intl": sum(l["frete_intl"] for l in linhas),
        "seguro": sum(l["seguro"] for l in linhas),
        "subtotal": sum(l["subtotal"] for l in linhas),
        "taxa_servico": sum(l["taxa_servico"] for l in linhas),
        "total_yuan": sum(l["total_yuan"] for l in linhas),
        "total_reais": sum(l["total_reais"] for l in linhas),
    }
    return linhas, totais
