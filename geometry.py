from math import sqrt, fabs, pow, atan2, pi
from enum import Enum
from typing import List, Optional

class Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def distance(self, pt: "Point") -> float:
        return sqrt(pow(self.x-pt.x, 2) + pow(self.y-pt.y, 2))
    
    def distance_sq(self, pt: "Point") -> float:
        return pow(self.x-pt.x, 2) + pow(self.y-pt.y, 2)
    
    def distance_manhattan(self, pt: "Point") -> float:
        return abs(self.x - pt.x) + abs(self.y - pt.y)
    
    def angle(self, pt: "Point") -> float:
        return atan2(pt.y - self.y, pt.x - self.x)*180/pi
    
    def cross(self, pt: "Point") -> float:
        return self.x*pt.y - self.y*pt.x
    
    def norm(self) -> float:
        return sqrt(self.x*self.x + self.y*self.y)
    
    def to_cv(self) -> tuple:
        return (self.x, self.y)
    
    def to_cv_int(self) -> tuple:
        return (int(self.x), int(self.y))
    
    def to_image_coords(self, w: int, h: int) -> "Point":
        return Point(self.x*w, self.y*h)
    
    def __sub__(self, other: "Point") -> "Point":
        return Point(self.x - other.x, self.y-other.y)
    
    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __mul__(self, other: float) -> "Point":
        return Point(self.x*other, self.y*other)
    
    def __truediv__(self, other: float) -> "Point":
        return Point(self.x/other, self.y/other)
    
    @property
    def xi(self) -> int:
        return int(self.x)

    @property
    def yi(self) -> int:
        return int(self.y)
    
    def __str__(self):
        return '{{x: {0}, y: {1}}}'.format(self.x, self.y)
    
    def __repr__(self):
        return self.__str__()

def order_points(points: List[Point]) -> List[Point]:
    """Ordena pontos em sentido horário.
    Adaptado de: https://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/"""
    tl = min(points, key=lambda pt: pt.y + pt.x)
    tr = min(points, key=lambda pt: pt.y - pt.x)
    br = max(points, key=lambda pt: pt.y + pt.x)
    bl = max(points, key=lambda pt: pt.y - pt.x)
    return [tl, tr, br, bl]

class Line:
    def __init__(self, pt1: Point, pt2: Point) -> None:
        self.pt1 = pt1
        self.pt2 = pt2

    def equation(self, x: float) -> float:
        slope = (self.pt2.y - self.pt1.y)/(self.pt2.x - self.pt1.x)
        return slope*(x - self.pt1.x) + self.pt1.y

    def point_is_below(self, pt: Point) -> bool:
        return pt.y > self.equation(pt.x)

    def point_is_above(self, pt: Point) -> bool:
        return not self.point_is_below(pt)

    def point_is_inside(self, pt: Point) -> bool:
        """Se esta linha faz parte de um polígono cujos vértices estão listados
        em sentido horário, esta função indica se pt está dentro do polígono com
        relação a esta linha."""
        p = (self.pt2.x-self.pt1.x)*(pt.y-self.pt1.y)-(self.pt2.y-self.pt1.y)*(pt.x-self.pt1.x)
        return p > 0

    def distance(self, pt: Point) -> float:
        return fabs((self.pt2.y - self.pt1.y)*pt.x - (self.pt2.x - self.pt1.x)*pt.y + self.pt2.x*self.pt1.y -
                    self.pt2.y*self.pt1.x)/sqrt(pow(self.pt2.y - self.pt1.y, 2) + pow(self.pt2.x - self.pt1.x, 2))

    def length(self) -> float:
        return self.pt1.distance(self.pt2)
    
    def intersection(self, line: 'Line') -> Point:
        x1 = self.pt1.x
        y1 = self.pt1.y
        x2 = self.pt2.x
        y2 = self.pt2.y
        x3 = line.pt1.x
        y3 = line.pt1.y
        x4 = line.pt2.x
        y4 = line.pt2.y
        inter_x = ((x1*y2 - y1*x2)*(x3 - x4) - (x1 - x2)*(x3*y4 - y3*x4))/((x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4))
        inter_y = ((x1*y2 - y1*x2)*(y3 - y4) - (y1 - y2)*(x3*y4 - y3*x4))/((x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4))
        return Point(inter_x, inter_y)
    
    def segment_intersection(self, line: 'Line') -> Optional[Point]:
        """Verifica se existe interseção entre dois segmentos de reta (o método intersection
        assume que as duas linhas são infinitas, aqui consideramos apenas o segmento de reta).
        Adaptado de: https://stackoverflow.com/a/565282/3489942"""
        #print(self)
        #print(line)
        #print('----')
        p = self.pt1
        q = line.pt1
        r = self.pt2 - self.pt1
        s = line.pt2 - line.pt1

        rxs = r.cross(s)
        qpr = (q-p).cross(r)
        qps = (q-p).cross(s)

        #print('p {} q {} r {} s {} rxs {} qpr {} qps {}'.format(p, q, r, s, rxs, qpr, qps))
        
        if rxs == 0:
            #Retas são colineares ou paralelas
            #No caso de retas colineares, poderíamos determinar uma região de interseção, mas
            #vamos ignorar esse caso por enquanto (aka pra sempre).
            return None
        
        t = qps/rxs
        u = qpr/rxs

        #print('t {} u {}'.format(t, u))

        if t >= 0 and t <= 1 and u >= 0 and u <= 1:
            return p + r*t
        else:
            return None

    def to_image_coords(self, w: int, h: int) -> 'Line':
        return Line(self.pt1.to_image_coords(w, h), self.pt2.to_image_coords(w, h))

    def __str__(self):
        return 'pt1: {} pt2: {}'.format(self.pt1, self.pt2)

class Polygon:
    def __init__(self, points: List[Point]):
        self.points = points
    
    def clip(self, polygon: 'Polygon') -> 'Polygon':
        """Utiliza polygon para cortar este polígono.
        Algoritmo Sutherland Hodgman: https://gamedevelopment.tutsplus.com/tutorials/understanding-sutherland-hodgman-clipping-for-physics-engines--gamedev-11917"""
        output_pts = self.points.copy() # type: List[Point]
        num_clip_planes = len(polygon.points)

        for i in range(num_clip_planes):
            if not output_pts:
                return None
            plane = Line(polygon.points[i-1], polygon.points[i])
            input_pts = output_pts
            output_pts = []
            starting_pt = input_pts[-1]

            for ending_pt in input_pts:
                start_in = plane.point_is_inside(starting_pt)
                end_in = plane.point_is_inside(ending_pt)

                if start_in and end_in:
                    output_pts.append(ending_pt)
                elif start_in and not end_in:
                    inter = plane.intersection(Line(starting_pt, ending_pt))
                    output_pts.append(inter)
                elif not start_in and end_in:
                    inter = plane.intersection(Line(starting_pt, ending_pt))
                    output_pts.append(inter)
                    output_pts.append(ending_pt)
                starting_pt = ending_pt
        
        if not output_pts:
            return None

        return Polygon(output_pts)
    
    def area(self) -> float:
        """Calcula a área do polígono.
        http://mathworld.wolfram.com/PolygonArea.html"""
        total = 0
        from_pt = self.points[-1]

        for to_pt in self.points:
            total = total + from_pt.x*to_pt.y - to_pt.x*from_pt.y
            from_pt = to_pt
            
        return total/2
    
    def to_image_coords(self, w: int, h: int, sort_clockwise = True) -> 'Polygon':
        """Converte as coordenadas deste polígono de percentual para o tamanho real da imagem.
        Opcionalmente ordena os pontos em sentido horário (para polígonos de quatro pontos)"""
        pts = [Point(pt.x*w, pt.y*h) for pt in self.points]
        if sort_clockwise:
            pts = order_points(pts)
        return Polygon(pts)

class Box:
    def __init__(self, pt1: Point, pt2: Point) -> None:
        self.pt1 = pt1
        self.pt2 = pt2

    def iou(self, other: 'Box') -> float:
        """Calcula a intersection over union (IoU) entre dois retângulos.
        Adaptado de: https://www.pyimagesearch.com/2016/11/07/intersection-over-union-iou-for-object-detection/"""
        x_a = max(self.pt1.xi, other.pt1.xi)
        y_a = max(self.pt1.yi, other.pt1.yi)
        x_b = min(self.pt2.xi, other.pt2.xi)
        y_b = min(self.pt2.yi, other.pt2.yi)

        inter_area = max(0, x_b - x_a + 1) * max(0, y_b - y_a + 1)
        box_a_area = (self.pt2.x - self.pt1.x + 1) * (self.pt2.y - self.pt1.y + 1)
        box_b_area = (other.pt2.x - other.pt1.x + 1) * (other.pt2.y - other.pt1.y + 1)
        iou = inter_area / float(box_a_area + box_b_area - inter_area)
        return iou

    @property
    def width(self) -> int:
        """Largura do box."""
        return abs(self.pt1.xi-self.pt2.xi)

    @property
    def height(self) -> int:
        """Altura do box."""
        return abs(self.pt1.yi-self.pt2.yi)

    @property
    def largest_dim(self) -> int:
        """Maior dimensão do box."""
        return max(self.width, self.height)

    @property
    def center(self) -> Point:
        """Centro do box."""
        return Point(self.pt1.x + self.width//2, self.pt1.y + self.height//2)
    
    @property
    def area(self) -> float:
        return self.width*self.height

    def distance(self, other: "Box") -> float:
        """Distância entre os centros de dois boxes."""
        return self.center.distance(other.center)

    def contains(self, other: "Box") -> bool:
        """Determina se este box contém o box passado no parâmetro `other`."""
        return self.pt1.x <= other.pt1.x and self.pt1.y <= other.pt1.y and \
            self.pt2.x >= other.pt2.x and self.pt2.y >= other.pt2.y
    
    def to_polygon(self) -> Polygon:
        pt1 = self.pt1
        pt2 = Point(self.pt2.x, self.pt1.y)
        pt3 = self.pt2
        pt4 = Point(self.pt1.x, self.pt2.y)
        return Polygon([pt1, pt2, pt3, pt4])