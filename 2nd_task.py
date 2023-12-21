def check_social_connections(connections: list[int]) -> str:
    number_of_connections = len(connections)
    counter_of_connections = number_of_connections - 1
    connections.sort(reverse=True)

    for i in range(number_of_connections):
        if not counter_of_connections:
            return "Yes"

        for j in range(i + 1, number_of_connections):
            if connections[i] > 0 and connections[j] > 0:
                connections[i] -= 1
                connections[j] -= 1
                counter_of_connections -= 1

    return "No"


list_of_connections = [1, 1, 10000, 1]
print(check_social_connections(list_of_connections))
