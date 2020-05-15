import io
import sys
import csv
import pprint
import traceback
from math import inf
from PyQt5 import uic
from random import randint
from math import pi, cos, sin
from collections import defaultdict
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QPainter, QColor, QFont, QIcon, QPen
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload,MediaFileUpload
from googleapiclient.discovery import build
from PyQt5.QtWidgets import *
from heapq import *


flag = True
flag_inf = False
floyd_falg = False
floyd_dist = None
choice_path_1 = None
choice_path_2 = None
dijkstra_path = None
dijkstra_cost = None
flag_dijkstra = False
falg_symmetric = False
falg_symm_csv = False
kol_versh = 0
sp_changed_csv = []
sp_changed = []
cost_of_path = {}
possible_path = {}
SCREEN_SIZE = [521, 541]

uifile_1 = 'FirstForm.ui'
form_1, base_1 = uic.loadUiType(uifile_1)
uifile_2 = 'ChoiceToGraph.ui'
form_2, base_2 = uic.loadUiType(uifile_2)
uifile_3 = 'CreateTable.ui'
form_3, base_3 = uic.loadUiType(uifile_3)
uifile_4 = 'ChangeCsv.ui'
form_4, base_4 = uic.loadUiType(uifile_4)
uifile_5 = 'CreatGraph.ui'
form_5, base_5 = uic.loadUiType(uifile_5)

    
class FirstForm(base_1, form_1):
    def __init__(self):
        super().__init__()
        self.open_form()

    def open_form(self):
        super(base_1, self).__init__()
        self.setupUi(self)
        self.pbt_create_table.clicked.connect(self.choice_to_graph)
        self.pbt_choice_csv.clicked.connect(self.open_csv)

    def choice_to_graph(self):
        self.choice_to_graph = ChoiceToGraph()
        self.choice_to_graph.show()
        self.close()
        
    def open_csv(self):
        self.open_csv = OpenCsv()
        self.open_csv.show()
        self.close()


class ChoiceToGraph(base_2, form_2):
    def __init__(self):
        super().__init__()
        self.open_form()

    def open_form(self):
        super(base_2, self).__init__()
        self.setupUi(self)
        self.pbt_continue.clicked.connect(self.continue_creat)
        self.pbt_back.clicked.connect(self.back)

    def continue_creat(self):
        global kol_versh
        kol_versh = self.spb_choice.value()
        self.create_table = CreateTable()
        self.create_table.show()
        self.close()

    def back(self):
        global kol_versh
        kol_versh = 0
        self.back_FirstForm = FirstForm()
        self.back_FirstForm.show()
        self.close()


class CreateTable(base_3, form_3):  
    def __init__(self):
        super().__init__()
        self.open_form()

    def open_form(self):
        super(base_3, self).__init__()
        self.setupUi(self)
        self.pbt_creat_graph.clicked.connect(self.creat_graph)
        self.pbt_back.clicked.connect(self.back)
        self.pbt_save_to_csv.clicked.connect(self.csv_dict_writer)
        self.rbt_symmetric.clicked.connect(self.symmetric)
        self.create_table()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget) 
        self.setLayout(self.layout)

    def create_table(self):
        self.tableWidget.setRowCount(kol_versh)
        self.tableWidget.setColumnCount(kol_versh)
        header = self.tableWidget.horizontalHeader()
        for i in range(kol_versh):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
            self.tableWidget.setItem(i, i, QTableWidgetItem("-"))
        self.tableWidget.itemChanged.connect(self.symmetric_changed)            

    def creat_graph(self):
        global cost_of_path, possible_path
        chet = '1'
        for i in range(self.tableWidget.rowCount()):
            path = []
            for j in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(i, j)
                if item is None:
                    path.append('')
                else:
                    path.append(item.text())
            cost_of_path.update({str(i + 1): path})
        for i in cost_of_path.values():
            path = []
            n = 0
            for j in i:
                n += 1
                if j != '0' and j != '-' and j != '':
                    path.append(n)                            
            possible_path.update({chet: path})
            chet = str(int(chet) + 1)
        self.create_graph = CreatGraph()
        self.create_graph.show()
        self.close()

    def symmetric(self):
        global falg_symmetric
        falg_symmetric = not falg_symmetric 

    def symmetric_changed(self, item):
        global sp_changed
        if falg_symmetric:
            if [item.row(), item.column()] not in sp_changed:
                sp_changed.append([item.column(), item.row()])
                self.tableWidget.setItem(item.column(), item.row(), QTableWidgetItem(item.text()))

    def csv_dict_writer(self):
        vse_path = []
        vse_path.append(list(range(kol_versh)))
        for i in range(self.tableWidget.rowCount()):
            path = []
            for j in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(i, j)
                if item is None:
                    path.append('')
                else:
                    path.append(item.text())
            vse_path.append(path)
        data = []
        fieldnames = vse_path[0]
        for values in vse_path[1:]:
            inner_dict = dict(zip(fieldnames, values))
            data.append(inner_dict)
        with open("save csvfile.csv", "w", newline='') as csvfile:
            writer = csv.DictWriter(csvfile, delimiter=',', fieldnames=fieldnames)
            for row in data:
                writer.writerow(row)
            
    def back(self):
        global cost_of_path, possible_path, falg_symmetric, sp_changed
        falg_symmetric = False
        sp_changed = []
        cost_of_path = {}
        possible_path = {}
        self.back_choice_to_graph = ChoiceToGraph()
        self.back_choice_to_graph.show()
        self.close()


class OpenCsv(base_4, form_4):
    def __init__(self):
        super().__init__()
        self.open_form()

    def open_form(self):
        global flag
        super(base_4, self).__init__()
        self.setupUi(self)
        self.pbt_continue_open.clicked.connect(self.continue_open)
        self.pbt_choice_file.clicked.connect(self.choice_file)
        self.pbt_choice_csv_file.clicked.connect(self.choice_csv_file)
        self.rbt_csv_change.clicked.connect(self.csv_change)
        self.pbt_save_csv.clicked.connect(self.saveToCsv)
        self.pbt_back.clicked.connect(self.back)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget) 
        self.setLayout(self.layout)
        flag = False

    def choice_csv_file(self):
        self.fname = QFileDialog.getOpenFileName(self, 'Выбрать csv файл',
                                    '', "Файл(*.csv)")[0]
        self.open_file(f'{self.fname}')

    def choice_file(self):
        self.fname = QFileDialog.getOpenFileName(self, 'Выбрать файл',
                                    '')[0]
        pp = pprint.PrettyPrinter(indent=4)
        SCOPES = ['https://www.googleapis.com/auth/drive']
        SERVICE_ACCOUNT_FILE = 'YL project-4da15c06ac06.json'
        credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('drive', 'v3', credentials=credentials)
        
        folder_id = '1lTCKCNrdiEsZwqYGOxr3TZvDwhWOdvJc'
        name = 'Some_file'
        file_path = self.fname
        file_metadata = {
                        'name': name,
                        'mimeType': 'application/vnd.google-apps.spreadsheet',
                        'parents': [folder_id]
                    }
        media = MediaFileUpload(file_path, resumable=True)
        r = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        pp.pprint(f'Скачанный файл: {r}')
        downloaded_file_id = r['id']

        file_id = downloaded_file_id
        request = service.files().export_media(fileId=file_id,
                                                     mimeType='text/csv') # формат выхода
        filename = 'Новая таблица(change formate).csv'
        fh = io.FileIO(filename, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))
            
        results_del = service.files().list(
            pageSize=10, 
            fields="nextPageToken, files(id, name, mimeType, parents, createdTime)",
            q="'yl-project-api@yl-project-258815.iam.gserviceaccount.com' in owners").execute()
        for i in results_del['files']:
            service.files().delete(fileId=i['id']).execute()

        results = service.files().list(pageSize=10,
                                       fields="nextPageToken, files(id, name, mimeType)").execute()
        nextPageToken = results.get('nextPageToken')
        while nextPageToken:
                nextPage = service.files().list(pageSize=10,
                                                fields="nextPageToken, files(id, name, mimeType, parents)",
                                                pageToken=nextPageToken).execute()
                nextPageToken = nextPage.get('nextPageToken')
                results['files'] = results['files'] + nextPage['files']
        print(len(results.get('files')))
        pp.pprint(results)
        results2 = service.files().list(
                pageSize=10, fields="nextPageToken, files(id, name, mimeType, parents, createdTime, permissions, quotaBytesUsed)").execute()
        pp.pprint(results2)

    def open_file(self, table_name):
        global cost_of_path, possible_path, kol_versh
        with open(f'{self.fname}', encoding="utf8") as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            chet = '1'
            for i in reader:
                path = []
                for j in i:
                        path.append(j)
                cost_of_path.update({chet: path})
                chet = str(int(chet) + 1)
            chet1 = '1'
            for i in cost_of_path.values():
                path = []
                n = 0
                for j in i:
                    n += 1
                    if j != '0' and j != '-' and j != '':
                        path.append(n)
                possible_path.update({chet1: path})
                chet1 = str(int(chet1) + 1)
        kol_versh = len(possible_path)
        self.tableWidget.setColumnCount(kol_versh)
        self.tableWidget.setRowCount(kol_versh)
        for i, row in enumerate(cost_of_path.values()):
            for j, elem in enumerate(row):
                if falg_symm_csv:
                    cost_of_path[str(j + 1)][i] = elem
                self.tableWidget.setItem(i, j, QTableWidgetItem(elem))
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.itemChanged.connect(self.symm_changed_csv)

    def saveToCsv(self):
        with open(f'{self.fname}', 'w', newline='') as csvfile:
            writer = csv.writer(
                csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            save_spis = []
            for i in range(self.tableWidget.rowCount()):
                spis = []
                for j in range(self.tableWidget.columnCount()):
                    item = self.tableWidget.item(i, j)
                    if item is not None:
                        spis.append(item.text())
                save_spis.append(spis)
            for i, row in enumerate(save_spis):
                if falg_symm_csv:
                    for j, elem in enumerate(row):
                        save_spis[i][j] = save_spis[j][i]
                writer.writerow(row)
        self.open_file(f'{self.fname}')

    def csv_change(self):
        global falg_symm_csv
        falg_symm_csv = not falg_symm_csv

    def symm_changed_csv(self, item):
        global sp_changed_csv
        if falg_symm_csv:
            if [item.row(), item.column()] not in sp_changed_csv:
                sp_changed_csv.append([item.column(), item.row()])
                self.tableWidget.setItem(item.column(), item.row(), QTableWidgetItem(item.text()))
        
    def continue_open(self):
        self.create_graph = CreatGraph()
        self.create_graph.show()
        self.close()

    def back(self):
        global kol_versh, cost_of_path, possible_path, flag, falg_symm_csv
        flag = True
        falg_symm_csv = False
        sp_changed_csv = []
        cost_of_path = {}
        possible_path = {}
        kol_versh = 0
        self.back_FirstForm = FirstForm()
        self.back_FirstForm.show()
        self.close()

        
class CreatGraph(base_5, form_5):
    def __init__(self):
        super().__init__()
        self.open_form()

    def open_form(self):
        super(base_5, self).__init__()
        self.setupUi(self)
        self.col1, self.col2, self.col3 = randint(0, 255), randint(0, 255), randint(0, 255)
        self.col4, self.col5, self.col6 = randint(0, 255), randint(0, 255), randint(0, 255)
        self.pbt_dijkstra_alg.clicked.connect(self.dijkstra_alg)
        self.pbt_floyd_alg.clicked.connect(self.floyd_alg)
        self.pbt_back.clicked.connect(self.back)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawGraph(event, qp)
        self.drawText(event, qp)
        qp.end()

    def xs(self, x):
        return x + SCREEN_SIZE[0] // 2

    def ys(self, y):
        return SCREEN_SIZE[1] // 2 - y

    def search_koord(self, startX, startY, endX, endY):
        Length = 15
        Height = 10
        vec_dX = endX - startX
        vec_dY = endY - startY
        Len = (vec_dX * vec_dX + vec_dY * vec_dY) ** 0.5
        vec_udX = vec_dX / Len
        vec_udY = vec_dY / Len
        perpX = -vec_udY
        perpY = vec_udX
        leftX = endX - Length * vec_udX + Height * perpX
        leftY = endY - Length * vec_udY + Height * perpY
        rightX = endX - Length * vec_udX - Height * perpX
        rightY = endY - Length * vec_udY - Height * perpY
        return leftX, leftY, rightX, rightY

    def drawGraph(self, event, qp):
        super().paintEvent(event)
        chet = 0
        RAD = 100 # длина стороны
        self.koordinate = []
        demo_nodes = [(RAD * cos(i * 2 * pi / kol_versh), RAD * sin(i * 2 * pi / kol_versh)) for i in range(kol_versh)]
        self.nodes = [(self.xs(node[0]), self.ys(node[1])) for node in demo_nodes]
        for i in self.nodes:
            pen = QPen(QColor(255, 0, 0), 1)
            qp.setPen(pen)
            qp.setBrush(QColor(255, 255, 255))
            qp.drawRect(i[0] - 15, i[1] - 15, 30, 30)
            self.koordinate.append([i[0] - 15, i[1] - 15, i[0] + 15, i[1] + 15])
        for i in possible_path.values():
            if len(i) != 0:
                for j in i:
                    startX, startY = self.nodes[chet][0], self.nodes[chet][1]
                    endX, endY  = self.nodes[j - 1][0], self.nodes[j - 1][1]
                    leftX, leftY, rightX, rightY = self.search_koord(startX, startY, endX, endY)
                    pen = QPen(QColor(self.col1, self.col2, self.col3), 2)
                    qp.setPen(pen)
                    qp.drawLine(startX, startY, endX, endY)
                    qp.drawLine(endX, endY, leftX, leftY)
                    qp.drawLine(endX, endY, rightX, rightY)
            chet += 1
        pen = QPen(QColor(20, 20, 20), 2)
        qp.setPen(pen)
        if dijkstra_path and flag_dijkstra:
            if len(dijkstra_path) == 2:
                qp.drawLine(self.nodes[int(dijkstra_path[0]) - 1][0],
                            self.nodes[int(dijkstra_path[0]) - 1][1],
                            self.nodes[int(dijkstra_path[1]) - 1][0],
                            self.nodes[int(dijkstra_path[1]) - 1][1])
                leftX, leftY, rightX, rightY = self.search_koord(self.nodes[int(dijkstra_path[0]) - 1][0], 
                                                                 self.nodes[int(dijkstra_path[0]) - 1][1],
                                                                 self.nodes[int(dijkstra_path[1]) - 1][0],
                                                                 self.nodes[int(dijkstra_path[1]) - 1][1])
                qp.drawLine(self.nodes[int(dijkstra_path[1]) - 1][0],
                            self.nodes[int(dijkstra_path[1]) - 1][1], leftX, leftY)
                qp.drawLine(self.nodes[int(dijkstra_path[1]) - 1][0],
                            self.nodes[int(dijkstra_path[1]) - 1][1], rightX, rightY)
            else:
                for i in dijkstra_path:
                    if dijkstra_path[len(dijkstra_path) - 1] != i:
                        qp.drawLine(self.nodes[int(i) - 1][0], self.nodes[int(i) - 1][1],
                                    self.nodes[int(dijkstra_path[dijkstra_path.index(i) + 1]) - 1][0],
                                    self.nodes[int(dijkstra_path[dijkstra_path.index(i) + 1]) - 1][1])
                        leftX, leftY, rightX, rightY = self.search_koord(self.nodes[int(i) - 1][0],
                                                                         self.nodes[int(i) - 1][1],
                                                                         self.nodes[int(dijkstra_path[dijkstra_path.index(i) + 1]) - 1][0],  
                                                                         self.nodes[int(dijkstra_path[dijkstra_path.index(i) + 1]) - 1][1])
                        qp.drawLine(self.nodes[int(dijkstra_path[dijkstra_path.index(i) + 1]) - 1][0],
                                    self.nodes[int(dijkstra_path[dijkstra_path.index(i) + 1]) - 1][1],
                                    leftX, leftY)
                        qp.drawLine(self.nodes[int(dijkstra_path[dijkstra_path.index(i) + 1]) - 1][0],
                                    self.nodes[int(dijkstra_path[dijkstra_path.index(i) + 1]) - 1][1],
                                    rightX, rightY)
        pen = QPen(QColor(20, 20, 20), 1)
        qp.setPen(pen)
        if choice_path_1:
            qp.setBrush(QColor(150, 255, 150))
            qp.drawRect(self.koordinate[int(choice_path_1) - 1][0],
                        self.koordinate[int(choice_path_1) - 1][1], 30, 30)
        if choice_path_2:
            qp.setBrush(QColor(255, 150, 150))
            qp.drawRect(self.koordinate[int(choice_path_2) - 1][0],
                        self.koordinate[int(choice_path_2) - 1][1], 30, 30)

    def drawText(self, event, qp):
        super().paintEvent(event)
        chet = 0
        qp.setPen(QColor(168, 34, 3))
        qp.setFont(QFont('Decorative', 20))
        for i in possible_path.keys():
            qp.drawText(self.nodes[chet][0] - 7, self.nodes[chet][1] + 9, i)
            chet += 1
        qp.setPen(QColor(self.col4, self.col5, self.col6))
        qp.setFont(QFont('Decorative', 15))
        if dijkstra_path and flag_dijkstra:
            qp.drawText(10, 20, f'Кратчайший путь от вершины {dijkstra_path[0]} до'
                        f' {dijkstra_path[len(dijkstra_path) - 1]}-й составляет {dijkstra_cost}.')
            qp.drawText(10, 50, f'{dijkstra_path}')
        elif flag_inf:
            qp.drawText(10, 20, 'inf')
        elif floyd_falg and floyd_dist:
            n = 20
            for i in floyd_dist:
                qp.drawText(10, n, f'{i}: {floyd_dist[i]}')
                n += 20

    def mousePressEvent(self, event):
        global choice_path_1, choice_path_2, flag_dijkstra, floyd_falg, flag_inf
        if (event.button() == Qt.LeftButton):
            for i in self.koordinate:
                if i[0] <= event.x() <= i[2] and i[1] <= event.y() <= i[3]:
                    if not choice_path_1: 
                        choice_path_1 = str(self.koordinate.index(i) + 1)
                    else:
                        choice_path_2 = str(self.koordinate.index(i) + 1)
        if (event.button() == Qt.RightButton):
            for i in self.koordinate:
                if i[0] <= event.x() <= i[2] and i[1] <= event.y() <= i[3]:
                    if choice_path_1 == str(self.koordinate.index(i) + 1) and choice_path_2 == None: 
                        choice_path_1 = None
                    elif choice_path_1 == str(self.koordinate.index(i) + 1) and choice_path_2 != None: 
                        choice_path_1 = choice_path_2
                        choice_path_2 = None
                    elif choice_path_2 == str(self.koordinate.index(i) + 1): 
                        choice_path_2 = None
        flag_dijkstra = False
        floyd_falg = False
        flag_inf = False
        self.update()

    def dijkstra_alg(self, event):
        global dijkstra_path, flag_dijkstra, dijkstra_cost, flag_inf
        if choice_path_1 and choice_path_2:
            dijkstra_sp = []
            chet = '1'
            for i in possible_path.values():
                if len(i) != 0:
                    for j in i:
                        dijkstra_sp.append((chet, str(j), int(cost_of_path[chet][j - 1])))
                    chet = str(int(chet) + 1)
            dict = defaultdict(list)
            for l, r, c in dijkstra_sp:
                dict[l].append((c, r))
            value, dist = [(0, choice_path_1, ())], {choice_path_1: 0}
            while value:
                (dijkstra_cost, node, dijkstra_path) = heappop(value) 
                if dijkstra_cost > dist[node]: continue
                dijkstra_path += (node, )
                if node == choice_path_2:
                    flag_dijkstra = True
                    break
                for w, n in dict.get(node, ()):
                    oldc = dist.get(n, float("inf"))
                    newc = dijkstra_cost + w
                    if newc < oldc:
                        dist[n] = newc 
                        heappush(value, (newc, n, dijkstra_path))
            if not flag_dijkstra:
                flag_inf = True
            self.update()

    def floyd_alg(self):
        global floyd_dist, floyd_falg, flag_dijkstra
        floyd_sl = {}
        chet = '1'
        for i in possible_path.values():
            if len(i) != 0:
                dict = {}
                for j in i:
                    dict.update({str(j): int(cost_of_path[chet][j - 1])})
                floyd_sl.update({chet: dict})
                chet = str(int(chet) + 1)
        floyd_dist = {}
        for u in floyd_sl:
            floyd_dist[u] = {}
            for v in floyd_sl:
                floyd_dist[u][v] = inf
            floyd_dist[u][u] = 0
            for neighbor in floyd_sl[u]:
                floyd_dist[u][neighbor] = floyd_sl[u][neighbor]
        for t in floyd_sl:
            for u in floyd_sl:
                for v in floyd_sl:
                    newdist = floyd_dist[u][t] + floyd_dist[t][v]
                    if newdist < floyd_dist[u][v]:
                        floyd_dist[u][v] = newdist
        flag_dijkstra = False
        floyd_falg = True
        self.update()

    def back(self):
        global choice_path_1, choice_path_2, flag_dijkstra, floyd_falg
        flag_inf = False
        floyd_falg = False
        falg_symmetric = False
        flag_dijkstra = False
        dijkstra_path = None
        dijkstra_cost = None
        choice_path_1 = None
        choice_path_2 = None
        floyd_dist = None
        if flag:
            self.back_create_table = CreateTable()
            self.back_create_table.show()
            self.close()
        else:
            self.back_open_csv = OpenCsv()
            self.back_open_csv.show()
            self.close()
            
def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("Oбнаружена ошибка !:", tb)

sys.excepthook = excepthook
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FirstForm()
    ex.show()
    sys.exit(app.exec())
