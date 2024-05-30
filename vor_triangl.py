import heapq

BORDER = [-(2 << 14), -(2 << 14), (2 << 14), (2 << 14)]

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    def getCircleCenter(cls, a, b, c):
        if ((b.x - a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y)) > 0:
            return None, None
        x1, y1, x2, y2, x3, y3 = a.x, a.y, b.x, b.y, c.x, c.y
        if x1 == x2:
            x2, y2, x3, y3 = x3, y3, x2, y2
        elif x2 == x3:
            x1, y1, x2, y2 = x2, y2, x1, y1
        if x1 == x2:
            return None, None
        m1, m2 = (y2 - y1) / (x2 - x1), (y3 - y2) / (x3 - x2)

        if m1 == m2:
            return None, None
        x = (m1 * m2 * (y1 - y3) + m2 * (x1 + x2) - m1 * (x2 + x3)) / 2 / (m2 - m1)
        try:
            y = -1 / m2 * (x - (x2 + x3) / 2) + (y2 + y3) / 2
        except ZeroDivisionError:
            y = -1 / m1 * (x - (x1 + x2) / 2) + (y1 + y2) / 2

        rad = ((x - x1)**2 + (y - y1)**2)**0.5
        return cls(x, y), x+rad


class Event:
    def __init__(self, x, point, arc):
        self.x = x
        self.point: Point = point
        self.arc: Arc = arc
        self.valid = True


class Arc:
    def __init__(self, center, prev=None, next=None):
        self.center = center
        self.prev = prev
        self.next = next
        self.event = None

        self.contour1: Edge = None
        self.contour2: Edge = None


class Edge:
    def __init__(self, point):
        self.start = point
        self.end = None
        self.verts = [None, None]

    def setEnd(self, end):
        if self.end:
            return
        self.end = end


class PriorityQueue:
    def __init__(self):
        self.queue = []
        self.count = 0
        self.entries = dict()

    def push(self, item):
        if item in self.entries:
            return
        self.count += 1
        entry = [item.x, self.count, item]
        self.entries[item] = entry
        heapq.heappush(self.queue, entry)

    def pop(self):
        while self.queue:
            p, count, item = heapq.heappop(self.queue)
            if item:
                del self.entries[item]
                return item
        raise Exception("empty queue")

    def top(self):
        item = self.pop()
        self.push(item)
        return item
    

class Vor:
    def __init__(self, points):
        self.result = []  
        self.arc = None  
        self.points = points
        self.result2 = []

        self.point_e = PriorityQueue()
        self.circle_e = PriorityQueue()

        for pts in sorted(points, key=lambda x: x[1]):
            point = Point(pts[0], pts[1])
            self.point_e.push(point)

    def process(self):
        while self.point_e.queue:
            if self.circle_e.queue and (self.point_e.top().x >= self.circle_e.top().x):
                self.process_circle()
            else:
                self.process_point()

        while self.circle_e.queue:
            self.process_circle()

        self.finish_edges()

        return self.result

    def process_point(self):
        point = self.point_e.pop()
        self.insert_arc(point)

    def process_circle(self):
        event = self.circle_e.pop()
        if event.valid:
            edge = Edge(event.point)
            self.result.append(edge)
            arc = event.arc
            if arc.prev:
                arc.prev.next = arc.next
                arc.prev.contour2 = edge
                edge.verts[0] = arc.prev
            if arc.next:
                arc.next.prev = arc.prev
                arc.next.contour1 = edge
                edge.verts[1] = arc.next
            if arc.contour1:
                arc.contour1.setEnd(event.point)
            if arc.contour2:
                arc.contour2.setEnd(event.point)
            if arc.prev:
                self.check_circle_event(arc.prev, event.x)
            if arc.next:
                self.check_circle_event(arc.next, event.x)

    def insert_arc(self, point):
        if self.arc == None:
            self.arc = Arc(point)
        else:
            cur = self.arc
            while cur:
                inter = self.crossing_lp(point, cur)
                if inter:
                    inter_next = self.crossing_lp(point, cur.next)
                    if cur.next and not inter_next:
                        cur.next.prev = Arc(cur.center, prev=cur, next=cur.next)
                        cur.next = cur.next.prev
                    else:
                        cur.next = Arc(cur.center, cur)
                    cur.next.contour2 = cur.contour2

                    cur.next.prev = Arc(point, prev=cur, next=cur.next)
                    cur.next = cur.next.prev
                    cur = cur.next

                    edge_1 = Edge(inter)
                    self.result.append(edge_1)
                    cur.prev.contour2 = cur.contour1 = edge_1
                    edge_1.verts = [cur.prev, cur.next]


                    edge_2 = Edge(inter)
                    self.result.append(edge_2)
                    cur.next.contour1 = cur.contour2 = edge_2
                    edge_2.verts = [cur.next, cur]

                    self.check_circle_event(cur, point.x)
                    self.check_circle_event(cur.prev, point.x)
                    self.check_circle_event(cur.next, point.x)
                    return
                cur = cur.next

            cur = self.arc
            while cur.next:
                cur = cur.next
            cur.next = Arc(point, cur)

            x = BORDER[0]
            y = (cur.next.center.y + cur.center.y) / 2
            start = Point(x, y)

            edge = Edge(start)
            cur.contour2 = cur.next.contour1 = edge
            edge.verts = [cur, cur.next]
            self.result.append(edge)
    
    def crossing_lp(self, point: Point, arc: Arc):
        if arc is None or point.x == arc.center.x:
            return None

        sides = [None, None]
        if arc.prev:
            sides[0] = self.crossing_pp(arc.prev, arc, point.x).y
        if arc.next:
            sides[1] = self.crossing_pp(arc, arc.next, point.x).y

        if (arc.prev is None or sides[0] <= point.y) and (arc.next is None or sides[1] >= point.y):
            crossing = [None, None]
            crossing[1] = point.y
            crossing[0] = (arc.center.x**2 + (arc.center.y - crossing[1])**2 - point.x**2) / 2 / (arc.center.x - point.x)
            return Point(*crossing)

        return None
    
    def crossing_pp(self, arc1, arc2, L):
        crossing = [None, None]
        if arc1.center.x == L:
            crossing[1] = arc1.center.y
            crossing[0] = (arc2.center.x ** 2 + (arc2.center.y - crossing[1]) ** 2 - L ** 2) / 2 / (arc2.center.x - L)
            return Point(*crossing)
        elif arc2.center.x == L:
            crossing[1] = arc2.center.y
            crossing[0] = (arc1.center.x ** 2 + (arc1.center.y - crossing[1]) ** 2 - L ** 2) / (2 * arc1.center.x - 2 * L)
            return Point(*crossing)
        
        eq1 = [
            1 / 2 / (arc1.center.x - L), 
            -arc1.center.y / (arc1.center.x - L),
            1 / 2 / (arc1.center.x - L) * (arc1.center.x ** 2 + arc1.center.y ** 2 - L ** 2)
        ]
        eq2 = [
            1 / 2 / (arc2.center.x - L), 
            -arc2.center.y / (arc2.center.x - L),
            1 / 2 / (arc2.center.x - L) * (arc2.center.x ** 2 + arc2.center.y ** 2 - L ** 2)
        ]
        final_eq = [eq1[0] - eq2[0], eq1[1] - eq2[1], eq1[2] - eq2[2]]
        
        if final_eq[0] == 0:
            crossing[1] = -final_eq[2] / final_eq[1]
            crossing[0] = eq1[0] * crossing[1] ** 2 + eq1[1] * crossing[1] + eq1[2]
            return Point(*crossing)
        
        crossing[1] = (-final_eq[1] - (final_eq[1] ** 2 - 4 * final_eq[0] * final_eq[2]) ** 0.5) / 2 / final_eq[0]
        crossing[0] = eq1[0] * crossing[1] ** 2 + eq1[1] * crossing[1] + eq1[2]
        return Point(*crossing)
    
    def check_circle_event(self, arc: Arc, x):
        if arc.event and arc.event.x != x:
            arc.event.valid = False
            arc.event = None

        if not (arc.prev and arc.next):
            return

        center, max_x = Point.getCircleCenter(arc.prev.center, arc.center, arc.next.center)
        if center and max_x > x:
            arc.event = Event(max_x, center, arc)
            self.circle_e.push(arc.event)
    

    def finish_edges(self):
        l = BORDER[2] + (BORDER[2] - BORDER[0]) + (BORDER[3] - BORDER[1])
        cur = self.arc

        while cur.next:
            if cur.contour2:
                p = self.crossing_pp(cur, cur.next, 2 * l)
                cur.contour2.setEnd(end=p)
            cur = cur.next