from typing import List


class Table:
    def __init__(self, lines):
        self.lines = lines

    # Linhas e colunas vão de 1 a 9
    def get_column(self, column: int) -> List[int]:
        if column > len(self.lines[0]) or column < 0:
            raise Exception("Coluna deve ser maior que 0 e menor que 10")
        return [line[column - 1] for line in self.lines]

    def get_line(self, line: int) -> List[int]:
        if line > len(self.lines) or line < 0:
            raise Exception("Linha deve ser maior que 0 e menor que 10")
        return self.lines[line - 1]

    # Quadrantes vão de 1 a 9, da esquerda para a direita e de cima para baixo
    # 1 2 3
    # 4 5 6
    # 7 8 9
    def get_block(self, block: int) -> List[List[int]]:
        if block > 9 or block < 0:
            raise Exception("Bloco deve ser maior que 0 e menor que 10")
        start_x = (block - 1) % 3 * 3
        start_y = (block - 1) // 3 * 3

        return [self.lines[start_y + i][start_x:start_x + 3] for i in range(3)]


if __name__ == '__main__':
    # save the next text as a vector
    test = [[5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9]]
    game = Table(test)
    print(game.get_block(1))
    print(game.get_block(2))
    print(game.get_block(3))
    print(game.get_block(4))
    print(game.get_block(5))
    print(game.get_block(6))
    print(game.get_block(7))
    print(game.get_block(8))
    print(game.get_block(9))

