import numpy as np


def convolve2D(base: np.ndarray, kernel: np.ndarray, paddingvalue=0):
    bx, by, kx, ky = *base.shape, *kernel.shape
    if (kx % 2) == 0 or (ky % 2) == 0 or kx > bx or ky > by:
        print("so geht das net")

    pad_x = int((kx - 1) / 2)
    pad_y = int((ky - 1) / 2)
    padded_base = np.pad(base, ((pad_x, pad_x), (pad_y, pad_y)), mode='constant', constant_values=paddingvalue)
    res = np.zeros((bx, by), dtype=kernel.dtype)
    for k in range(kx):
        for l in range(ky):
            res[...] += kernel[k, l] * padded_base[k:k + bx, l: l + by]
    return res


def get_sourrounding_wall_count_map(temp_map):
    kernel = np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]])
    return convolve2D(temp_map, kernel, 1)


def map_generator(x_dim, y_dim):
    random_treshold = 25
    map_state = np.random.randint(0, 100, (x_dim - 2, y_dim - 2))
    map_state = [[1 if a_ < random_treshold else 0 for a_ in row] for row in map_state]
    map_state = np.pad(map_state, (1, 1), 'constant', constant_values=(1, 1))

    def smooth_map(map):
        copy = np.copy(map)
        wall_count = get_sourrounding_wall_count_map(map)
        for x in range(0, x_dim):
            for y in range(0, y_dim):
                if wall_count[x, y] > 4:
                    copy[x][y] = 1
                elif wall_count[x, y] < 2:
                    copy[x][y] = 0
        return copy

    map_state = smooth_map(map_state)

    return map_state