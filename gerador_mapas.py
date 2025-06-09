import sys
import subprocess
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QTextEdit, 
                            QVBoxLayout, QHBoxLayout, QWidget, QLabel, QMessageBox,
                            QFrame, QSplitter)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont, QIcon, QDesktopServices

class GeradorMapas(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Configuração da janela principal
        self.setWindowTitle('Gerador de Mapas')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            QLabel {
                font-weight: bold;
                color: #333;
            }
        """)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Título
        title_label = QLabel('Gerador de Mapas')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont('Arial', 18))
        title_label.setStyleSheet("margin-bottom: 20px; color: #2E7D32;")
        main_layout.addWidget(title_label)
        
        # Layout para os botões
        button_layout = QHBoxLayout()
        
        # Botão para gerar mapa com raio
        self.btn_com_raio = QPushButton('Gerar Mapa COM Raio')
        self.btn_com_raio.setMinimumHeight(50)
        self.btn_com_raio.clicked.connect(lambda: self.mostrar_entrada_dados('com_raio'))
        button_layout.addWidget(self.btn_com_raio)
        
        # Botão para gerar mapa sem raio
        self.btn_sem_raio = QPushButton('Gerar Mapa SEM Raio')
        self.btn_sem_raio.setMinimumHeight(50)
        self.btn_sem_raio.setStyleSheet("background-color: #2196F3;")
        self.btn_sem_raio.clicked.connect(lambda: self.mostrar_entrada_dados('sem_raio'))
        button_layout.addWidget(self.btn_sem_raio)
        
        main_layout.addLayout(button_layout)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("margin-top: 20px; margin-bottom: 20px;")
        main_layout.addWidget(separator)
        
        # Área de entrada de dados
        self.input_label = QLabel('Insira os dados brutos:')
        self.input_label.setVisible(False)
        main_layout.addWidget(self.input_label)
        
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Cole aqui os dados brutos no formato:\nLatitude -23,40 Longitude -46,32 Cidade (+5 km), Outra Cidade (+20 km), ...")
        self.text_input.setVisible(False)
        main_layout.addWidget(self.text_input)
        
        # Botão para processar
        self.btn_processar = QPushButton('Processar e Gerar Mapa')
        self.btn_processar.setMinimumHeight(50)
        self.btn_processar.setStyleSheet("background-color: #FF9800;")
        self.btn_processar.clicked.connect(self.processar_dados)
        self.btn_processar.setVisible(False)
        main_layout.addWidget(self.btn_processar)
        
        # Área de status
        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #1565C0; margin-top: 20px;")
        main_layout.addWidget(self.status_label)
        
        # Botão para abrir o mapa gerado
        self.btn_abrir_mapa = QPushButton('Abrir Mapa Gerado')
        self.btn_abrir_mapa.setMinimumHeight(50)
        self.btn_abrir_mapa.setStyleSheet("background-color: #9C27B0;")
        self.btn_abrir_mapa.clicked.connect(self.abrir_mapa)
        self.btn_abrir_mapa.setVisible(False)
        main_layout.addWidget(self.btn_abrir_mapa)
        
        # Variável para armazenar o tipo de mapa atual
        self.tipo_mapa = None
        self.arquivo_mapa = None
        
    def mostrar_entrada_dados(self, tipo):
        self.tipo_mapa = tipo
        self.input_label.setVisible(True)
        self.text_input.setVisible(True)
        self.btn_processar.setVisible(True)
        self.status_label.setText('')
        self.btn_abrir_mapa.setVisible(False)
        
        # Exemplo de dados para facilitar o uso
        exemplo = """
Latitude -23,40 Longitude -46,32 Arujá (+5 km), Atibaia (+20 km), Latitude -23,50 Longitude -46,85 Barueri (+3 km), Bragança Paulista (+20 km), Campinas (+20 km), Latitude -23,47 Longitude -46,53 Guarulhos (+5 km)
"""
        self.text_input.setPlaceholderText(exemplo.strip())
        
    def processar_dados(self):
        dados = self.text_input.toPlainText().strip()
        if not dados:
            QMessageBox.warning(self, "Dados Vazios", "Por favor, insira os dados brutos para gerar o mapa.")
            return
        
        try:
            # Determinar qual script executar
            script_original = None
            if self.tipo_mapa == 'com_raio':
                script_original = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                          "Localização", "gerar_mapa_com_raio.py")
                self.arquivo_mapa = "mapa_com_raios.html"
            else:
                script_original = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                          "Localização", "gerar_mapa_sem_raio.py")
                self.arquivo_mapa = "mapa_com_pinos_personalizados.html"
            
            # Criar um script temporário com os dados embutidos
            temp_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_script.py")
            
            # Ler o script original
            with open(script_original, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Substituir os dados brutos diretamente no script
            if self.tipo_mapa == 'com_raio':
                content = content.replace('dados_brutos = """', f'dados_brutos = """{dados}\n')
            else:
                content = content.replace('raw_data = """', f'raw_data = """{dados}\n')
            
            # Salvar o script temporário
            with open(temp_script, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Executar o script
            self.status_label.setText("Processando dados e gerando mapa...")
            QApplication.processEvents()
            
            # Executar o script temporário
            result = subprocess.run(
                [sys.executable, temp_script],
                capture_output=True,
                text=False
            )
            
            # Decodificar manualmente com tratamento de erros
            stdout = result.stdout.decode('cp1252', errors='replace') if result.stdout else ""
            stderr = result.stderr.decode('cp1252', errors='replace') if result.stderr else ""
            
            if result.returncode == 0:
                self.status_label.setText("Mapa gerado com sucesso!")
                self.btn_abrir_mapa.setVisible(True)
            else:
                self.status_label.setText("Erro ao gerar o mapa.")
                QMessageBox.critical(self, "Erro", f"Erro ao gerar o mapa:\n{stderr}")
            
            # Limpar o script temporário
            if os.path.exists(temp_script):
                os.remove(temp_script)
                
        except Exception as e:
            self.status_label.setText(f"Erro: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro:\n{str(e)}")
    
# Este método não é mais necessário, pois agora estamos usando uma abordagem diferente
    
    def abrir_mapa(self):
        try:
            mapa_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.arquivo_mapa)
            if os.path.exists(mapa_path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(mapa_path))
            else:
                QMessageBox.warning(self, "Arquivo não encontrado", 
                                   f"O arquivo {self.arquivo_mapa} não foi encontrado.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir o mapa:\n{str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GeradorMapas()
    ex.show()
    sys.exit(app.exec_())