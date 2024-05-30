import argparse
import matplotlib.pyplot as plt
import random

from vor_triangl import Vor


def generate_random_points(count, x_range, y_range):
    return [[random.uniform(x_range[0], x_range[1]), random.uniform(y_range[0], y_range[1])] for _ in range(count)]


def main(input_file, output_file, points_number, show_vor = False):
    if input_file is None:
        x_range = (10, 250)
        y_range = (10, 250)
        points = generate_random_points(points_number, x_range, y_range)
    else:
        points = []
        with open(input_file, 'r') as infile:
            for line in infile:
                pnts = line.split()
                points.append([int(pnts[0]), int(pnts[1])])

    min_x = min(point[0] for point in points)
    min_y = min(point[1] for point in points)
    max_x = max(point[0] for point in points)
    max_y = max(point[1] for point in points)
    x_a = max_x - min_x
    y_a = max_y - min_y
    min_x -= x_a * 0.05
    min_y -= y_a * 0.05
    max_x += x_a * 0.05
    max_y += y_a * 0.05
    points += [[min_x, min_y], [max_x, min_y], [min_x, max_y], [max_x, max_y]]
    
    vor = Vor(points)
    vor.process()

    with open(output_file, 'w') as outfile:
        for edge in vor.result:
            if show_vor:
                plt.plot([edge.start.x, edge.end.x], [edge.start.y, edge.end.y], color='orange')
            start = edge.verts[0].center
            end = edge.verts[1].center
            plt.plot([start.x, end.x], [start.y, end.y], color='blue')
            outfile.write(f"[({start.x}, {start.y}), ({end.x}, {end.y})]\n")

    x_coords, y_coords = zip(*[(p[0], p[1]) for p in points])
    plt.scatter(x_coords, y_coords, color='red', zorder=2)
    
    plt.xlim(min_x, max_x)  
    plt.ylim(min_y, max_y)  
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Обробка файлів")
    parser.add_argument('-i', '--input', default=None, help="Файл вхідних даних")
    parser.add_argument('-o', '--output', default='triangl_edges.txt', help="Файл вихідних даних")
    parser.add_argument('-n', '--number', default=35, help="Кількість автоматично згенерованих точок")
    parser.add_argument('-v', '--voronyi', action='store_true', help="Відображати діаграму Вороного")

    args = parser.parse_args()

    main(args.input, args.output, args.number, args.voronyi)






