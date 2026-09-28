class Erro(Exception):

    def __init__(self, msg: str = ''):
        self.msg = msg
        super().__init__(msg)


class NaoEncontrado(Erro):
    pass


class Duplicado(Erro):
    pass


class NaoAlterado(Erro):
    pass


class IdInvalido(Erro):
    pass


class FalhaAutenticacao(Erro):
    pass


class SemPermissao(Erro):
    pass


class FalhaAPIExterna(Erro):
    pass
