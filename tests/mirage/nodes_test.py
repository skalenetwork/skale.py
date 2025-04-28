def test_get(mirage):
    node = mirage.nodes.get(1)
    assert node is not None
    print(node)
    assert node.id == 1
