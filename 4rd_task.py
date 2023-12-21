class TreeNode:
    def __init__(self, name, price, children=None):
        self.name = name
        self.price = price
        self.children = children if children else []


def find_min_cost_subtree(node, target_names):
    if node is None:
        return None

    # Рекурсивно ищем минимальные поддеревья во всех дочерних узлах
    subtrees = [find_min_cost_subtree(child, target_names) for child in node.children]

    # Проверяем, содержатся ли все целевые имена в текущем узле и его поддеревьях
    current_names = set([node.name])
    current_cost = node.price
    for subtree in subtrees:
        if subtree:
            current_names.update(subtree[0])
            current_cost += subtree[1]

    if set(target_names).issubset(current_names):
        # Если текущий узел и его поддеревья содержат все целевые имена,
        # возвращаем информацию о текущем поддереве (имена, стоимость)
        return (current_names, current_cost)

    # Иначе возвращаем поддерево с бесконечной стоимостью
    return (set(), float("inf"))


# Пример использования
root = TreeNode("A", 5, [TreeNode("B", 3), TreeNode("C", 7, [TreeNode("D", 2), TreeNode("E", 8)]), TreeNode("F", 4)])

target_names = ["A", "B", "D"]
result = find_min_cost_subtree(root, target_names)
print("Минимальное поддерево:", result[0])
print("Минимальная стоимость:", result[1])
