"""
Testes rápidos de calculo.py, usando o exemplo que está escrito na própria
planilha (linha 39): peso total 2100g, primário 20¥, secundário 50¥ -> 120¥.
"""
from calculo import frete_internacional_total, calcular_produto, calcular_pedido


def test_frete_internacional_exemplo_da_planilha():
    assert frete_internacional_total(2100, 20, 75) == 20 + 2 * 75


def test_frete_internacional_ate_1kg():
    assert frete_internacional_total(1000, 217, 75) == 217
    assert frete_internacional_total(500, 217, 75) == 217


def test_calcular_produto_bate_com_premissas_padrao():
    # Premissas padrão da planilha: seguro 6%, taxa 3%, cotação 1.2
    r = calcular_produto(
        preco=100, frete_interno=10, peso_g=500, peso_total_g=500,
        frete_intl_total=217, seguro_pct=0.06, taxa_servico_pct=0.03, cotacao=1.2,
    )
    # frete_intl = (500/500)*217 = 217
    assert r["frete_intl"] == 217
    # seguro = (100+10+217)*0.06 = 19.62
    assert round(r["seguro"], 2) == 19.62
    # subtotal = 100+10+217+19.62 = 346.62
    assert round(r["subtotal"], 2) == 346.62
    # taxa = 346.62*0.03 = 10.3986
    assert round(r["taxa_servico"], 4) == round(346.62 * 0.03, 4)
    total_yuan = 346.62 + round(346.62 * 0.03, 4)
    assert round(r["total_yuan"], 2) == round(total_yuan, 2)
    assert round(r["total_reais"], 2) == round(total_yuan * 1.2, 2)


class _FakePedido:
    def __init__(self, produtos, **premissas):
        self.produtos = produtos
        self.peso_primario = premissas.get("peso_primario", 217)
        self.peso_secundario = premissas.get("peso_secundario", 75)
        self.seguro_pct = premissas.get("seguro_pct", 0.06)
        self.taxa_servico_pct = premissas.get("taxa_servico_pct", 0.03)
        self.cotacao = premissas.get("cotacao", 1.2)


class _FakeProduto:
    def __init__(self, preco, frete_interno, peso_g):
        self.preco = preco
        self.frete_interno = frete_interno
        self.peso_g = peso_g


def test_calcular_pedido_rateia_frete_por_peso():
    produtos = [_FakeProduto(100, 0, 400), _FakeProduto(50, 0, 600)]
    pedido = _FakePedido(produtos)
    linhas, totais = calcular_pedido(pedido)
    assert totais["peso_total"] == 1000
    assert totais["frete_intl_total"] == 217  # <= 1000g, só o primário
    # fatia proporcional ao peso
    assert linhas[0]["frete_intl"] == round(400 / 1000 * 217, 2)
    assert linhas[1]["frete_intl"] == round(600 / 1000 * 217, 2)


if __name__ == "__main__":
    import sys
    import inspect

    funcs = [f for name, f in list(globals().items()) if name.startswith("test_")]
    falhas = 0
    for f in funcs:
        try:
            f()
            print(f"OK   {f.__name__}")
        except AssertionError as e:
            falhas += 1
            print(f"FAIL {f.__name__}: {e}")
    sys.exit(1 if falhas else 0)
