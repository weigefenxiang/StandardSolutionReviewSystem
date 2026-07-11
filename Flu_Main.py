# coding:utf-8  
"""====================================================
Standard solution calculation and audit system
Standard Solution Review System

Author: mighty
Contact: weigefenxiang@gmail.com
Copyright : © 2025 weige All Rights Reserved.
Created: 2025-04
Description:
    Standard solution calculation and review software,
    Used for standard solution calculation and data review

Developed with:
-Python
- PyQt6
- QFluentWidgets
-SQLite

This project is built based on the open source framework QFluentWidgets.
Follow its open source license.

Copyright © 2025 Weiwu
All Rights Reserved.
===================================================="""
# ==============================
#Software information

# ==============================

APP_NAME = "Standard Solution Review System"
APP_NAME = "标准溶液计算审核"
APP_VERSION = "V1.0.0.3"
APP_AUTHOR = "Wei.G"
APP_COPYRIGHT = "© 2025 Wei.G"
LOGO = "Wei.G-favicon_little.png"

import sys,os,sqlite3,math
from pathlib import Path
from typing import List, Tuple, Optional, Dict,TypedDict
from PyQt6.QtCore import Qt, QUrl, QDate, QSize, pyqtSlot
from PyQt6.QtGui import QIcon, QDesktopServices, QShortcut, QKeySequence
from PyQt6.QtWidgets import (QApplication, QFrame, QHBoxLayout,QVBoxLayout, QWidget, QGridLayout, QLineEdit)
from qfluentwidgets import (NavigationItemPosition, MessageBox, setTheme, Theme, SplitFluentWindow,SubtitleLabel,
                            InfoBar,InfoBarIcon, InfoBarPosition, FluentIcon, 
                            FlowLayout,PushButton,FastCalendarPicker,ComboBox,BodyLabel,
                            FastCalendarPicker,FluentIcon as FIF,ComboBox,
                            NavigationAvatarWidget, SubtitleLabel, setFont)
from decimal import Decimal, getcontext
from logTool import setup_logging

#Configure Decimal precision
getcontext().prec = 10

logger = setup_logging()

#Merged and packaged directory address
def get_exepack_dir():
    exe_real_dir = os.path.dirname(os.path.abspath(__file__))
    return exe_real_dir

#Get the current directory address when Nuitka exe is running
def get_exe_real_dir():
    return Path(sys.argv[0]).absolute().parent

#OneFile decompression directory
RUN_DIR = Path(__file__).resolve().parent
#directory where exe is located
EXE_DIR = Path(sys.argv[0]).resolve().parent
icon_path = str(
    RUN_DIR / "resource" / LOGO
)

avatar_path = str(
    RUN_DIR / "resource" / "deathNote.png"
)

#Get current folder path
base_dir = get_exe_real_dir()
base_packexe_dir = get_exepack_dir()
dbpath = str(
    RUN_DIR / "VolumeCorrectionValue.db"
)
today = QDate.currentDate()

# ==============================
#Global constant definition (centralized management configuration)
# ==============================
class AppConfig:
    """Apply global configuration"""
    #Window configuration
    WINDOW_SIZE: Tuple[int, int] = (960, 800)
    WINDOW_TITLE: str = APP_NAME
    WINDOW_ICON: str = ":/qfluentwidgets/images/logo.png"
    #Style configuration
    DARK_THEME: Theme = Theme.DARK
    LABEL_BG_COLOR: str = "#121212"
    INPUT_MAX_HEIGHT: int = 34
    INPUT_MIN_HEIGHT: int = 31
    INPUT_FONT_SIZE: int = 13
    GRID_COL_MIN_WIDTH: int = 60
    
    #Drop down box option configuration
    CONCENTRATION_OPTIONS: List[str] = (
        '标液浓度', '0.05 or less', '0.1 or 0.2', '0.5', '1'
    )
    SOLUTION_TYPE_OPTIONS: List[str] = (
        '标液种类', '水或水溶液', "盐酸", "氢氧化钠", "高锰酸钾", "硝酸银",
        "硫代硫酸钠", "氯化锌", "EDTA", "硫酸", "碳酸钠", "氢氧化钾-乙醇"
    )
    PREPARER_OPTIONS: List[str] = ('配置人', '汤妹', '王志鑫', "龚金梅")
    
    #Form prompt text
    FORM_PLACEHOLDERS: Dict[str, str] = {
        'weight': "称取质量 g",
        'volume': "配制体积 L",
        'calibration': "GB/T 601",
        'dry_condition': "干燥条件",
        'temperature': "℃",
        'molar_mass': "204.22",
        'main_calibrator': "主标人：",
        'secondary_calibrator': "副标人："
    }

    class TitrantInfo(TypedDict):
        """Reference material information corresponding to the titrant"""
        #Reference substance name (more standardized term)
        reference_substance: str  
        # 摩尔质量（单位：g/mol，保留精确小数）
        molar_mass: float         

    #The name of the titrant and its molar mass of the calibration substance
    TypeTitrantList: Dict[str, TitrantInfo] = {
                '盐酸':{'name':'无水碳酸钠','MolarMass':52.994},
                '氢氧化钠':{'name':'邻苯二甲酸氢钾','MolarMass':204.22},
                '高锰酸钾':{'name':'草酸钠','MolarMass':66.999},
                '硝酸银':{'name':'氯化钠','MolarMass':58.442},
                '硫代硫酸钠':{'name':'重铬酸钾','MolarMass':49.031},
                '氯化锌':{'name':'EDTA','MolarMass':0.05},
                'EDTA':{'name':'氯化锌','MolarMass':81.39},
                '硫酸':{'name':'无水碳酸钠','MolarMass':52.994},
                '碳酸钠':{'name':'无水碳酸钠','MolarMass':52.994},
                '氢氧化钾-乙醇':{'name':'邻苯二甲酸氢钾','MolarMass':204.22}
                }
    
#Determine the number of digits after the decimal point
def count_decimal_places(num):
    num_str = str(num)
    if '.' in num_str:
        return len(num_str.split('.')[1])
    else:
        return 0   

class dbtool():
    """Database tools"""
    def __init__(self, path):
        try:
            self.conn = sqlite3.connect(path, check_same_thread=False)
            #Support access by column name
            self.conn.row_factory = sqlite3.Row  
            self.cur = self.conn.cursor()
            logger.info(f"数据库加载成功，路径：{path}")
        except Exception as e:
            logger.error(f"数据库加载失败：{str(e)}，路径：{path}")
            raise
        
    def __del__(self):
        """Destructor: close the database connection"""
        try: 
            # 判断对象 obj 是否存在名为 'conn'（字符串形式）的属性 / 方法，返回 True（存在）或 False（不存在）。
            if hasattr(self, 'conn') and self.conn:
                self.conn.commit()
                self.cur.close()
                self.conn.close()
                logger.info("数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库失败：{str(e)}")
# ==============================
#Custom control encapsulation (high cohesion)
# ==============================
class NewQLineEdit(QLineEdit):
    """Standardized single-line input box (based on FluentTextEdit)"""
    def __init__(self, parent: Optional[QWidget] = None, fixed_width: Optional[int] = None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMaximumHeight(AppConfig.INPUT_MAX_HEIGHT)
        #Set font size
        setFont(self, AppConfig.INPUT_FONT_SIZE)  
        #minimum height
        self.setMinimumHeight(AppConfig.INPUT_MIN_HEIGHT) 
        #maximum height
        self.setMaximumHeight(AppConfig.INPUT_MAX_HEIGHT) 
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if fixed_width:
            self.setFixedWidth(fixed_width)
        self.setStyleSheet(f"""
            NewQLineEdit {{
                text-align: center;  /* 文字居中 */
                color: white;      /* 文字白色 */
                background-color: #000000;  /* 背景黑色 */
                border-radius: 3px;  /* 轻微圆角 */
            }}
        """)

class SectionLabel(BodyLabel):
    """用于“主标/副标”等区块标题的标签（背景自适应文字）"""
    #Use blue tones in the interface
    def __init__(self, text: str, parent=None, bg_color="#1E40AF"):  
        super().__init__(parent)
        self.setText(text)
        self.setStyleSheet(f"""
            SectionLabel {{
                background-color: {bg_color};
                border-radius: 3px;  /* 轻微圆角 */
                padding: 2px 30px;  /* 左右各8px内边距，扩展背景宽度 */
                font-weight: bold;  /* 加粗突出标题 */
            }}
        """)
        # color: white;  /* 白色文字更醒目 */
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

class StyledLabel(BodyLabel):
    """Labels with custom backgrounds"""
    def __init__(self, text: str, parent: Optional[QWidget] = None, bg_color: str = AppConfig.LABEL_BG_COLOR):
        super().__init__(parent)
        self._init_style(bg_color)
        self.setText(text)
    
    def _init_style(self, bg_color: str):
        """Initialize label style"""
        self.setContentsMargins(0, 0, 0, 0)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #-------------------------- Core: Set background color --------------------------
        self.setStyleSheet(f"""
            StyledLabel {{
                background-color: {bg_color};
                color: #E0E0E0;      /* 文本颜色（适配暗主题，可选）*/
                border-radius: 4px;  /* 圆角    优化视觉效果 */
                padding: 4px 0;      /* 避免文本贴边 */
            }}
        """)
        # /* border: 1px solid #444444;  /* 边框（可选，增加区分度）*/
        # padding: 2px 0;               /* 上下内边距（让文本不贴边，可选）*/

        
            
class Widget(QFrame):
    def __init__(self, text:str, parent = None):
        super().__init__(parent=parent)
        #Subtitle text label
        self.label = SubtitleLabel(text, self)  
        #QHBoxLayout horizontal layout
        self.hBoxLayout = QHBoxLayout(self) 

        #Set font
        setFont(self.label, 24) 
        #setAlignment QLabel's alignment is horizontally and vertically centered at the same time AlignCenter is centered
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        self.hBoxLayout.addWidget(self.label,1,Qt.AlignmentFlag.AlignCenter)
        self.setObjectName(text.replace(' ','-'))

        #!IMPORTANT: leave some space for title bar Leave some space for title bar
        #Top left, bottom right Left, top, right and bottom margins
        self.hBoxLayout.setContentsMargins(0, 32, 0, 0) 


class MainWidget(QWidget):
    """Main Page Component - Standard Solution Record Management""" 
    def __init__(self, text:str, parent = None):
        super().__init__(parent=parent)
        self.init_ui()
        self.setObjectName(text.replace(' ', '-'))
        # self.load_css_style()
        
        #Initialize startup default settings
        self._DefaultBegin()
        
        # 槽事件
        #Obtain the molar mass of the standard material based on different standard solutions
        self.comboBox0_2_03.currentTextChanged.connect(self._getMolarMass)    
        #Obtain the molar mass of the standard material based on different standard solutions
        self.textedit0_3_0402AND05.editingFinished.connect(self.textChange)    

    def textChange(self):
        print(self.textedit0_3_0402AND05.text())
        self.textedit0_3_0406AND09.setText(self.textedit0_3_0402AND05.text())
        self.textedit0_3_0406AND09.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
    def createInfoInfoBar(self,content="My name is kira yoshikake, 33 years old. Living in the villa area northeast of duwangting, unmarried. I work in Guiyou chain store. Every day I have to work overtime until 8 p.m. to go home. I don't smoke. The wine is only for a taste. Sleep at 11 p.m. for 8 hours a day. Before I go to bed, I must drink a cup of warm milk, then do 20 minutes of soft exercise, get on the bed, and immediately fall asleep. Never leave fatigue and stress until the next day. Doctors say I'm normal.",duration=2000):
        w = InfoBar(
            icon=InfoBarIcon.INFORMATION,
            title='Title',
            content=content,
            # vertical layout
            orient=Qt.Orientation.Vertical,    
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=duration,
            parent=self
        )
        w.addWidget(PushButton('Action'))
        w.show()
        
    def createSuccessInfoBar(self,content="With respect, let's advance towards a new stage of the spin.",duration=2000):
        """Tips for success"""
        InfoBar.success(
            title='Success',
            content=content,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            # position='Custom',   # NOTE: use custom info bar manager
            duration=duration,
            parent=self
        )

    def createWarningInfoBar(self,content="Believe in the spin, just keep believing!",duration=2000):
        """Warning"""
        InfoBar.warning(
            title='Warning',
            orient=Qt.Orientation.Horizontal,
            # disable close button
            isClosable=False,   
            position=InfoBarPosition.TOP_LEFT,
            duration=duration,
            parent=self
        )

    def createErrorInfoBar(self,content="迂回路を行けば最短ルート。",duration=5000):
        """Error message"""
        InfoBar.error(
            title='Error',
            content=content,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            # won't disappear automatically
            duration=duration,    
            parent=self
        )

    def createCustomInfoBar(self,content="人間讃歌は「勇気」の讃歌ッ！！ 人間のすばらしさは勇気のすばらしさ！！"):
        # 
        w = InfoBar.new(
            icon=FluentIcon.GITHUB,
            content="功能开发中.......",
            title=APP_AUTHOR,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM,
            duration=2000,
            parent=self
        )

    def createDeskTopBottomRightInfoBar(self,content="Battery is 64%"):
        """Tips in the lower right corner of the desktop"""
        InfoBar.warning(
            title='Plugged Out Notify',
            orient=Qt.Orientation.Vertical,
            position=InfoBarPosition.BOTTOM_RIGHT,
            parent=InfoBar.desktopView()
        )

    def init_ui(self):
        """Initialize interface layout and controls"""
        #00 vertical distribution
        self.qvBoxlayout0 = QVBoxLayout(self)    
        #Set control spacing
        self.qvBoxlayout0.setSpacing(5)  

        #title area
        #00 vertically distributed first row
        self.widget0_1 = QWidget(self) 
        #Set maximum height to 40
        self.widget0_1.setMaximumSize(QSize(16777215, 40)) 
        # self.widget0_1.setObjectName("widget1")
        #00_1 horizontal distribution
        self.horizontalLayout0_1 = QHBoxLayout(self.widget0_1) 
        self.label_title0_1_1 = SubtitleLabel('标准溶液原始记录审核', parent=self.widget0_1)
        # self.label_title = QLabel(parent=self.widget0_1)
        #00_1 Horizontal Distribution_Add Title
        self.horizontalLayout0_1.addWidget(self.label_title0_1_1)   

        #Main content area - Part 1
        #00 vertically distributed second row
        self.widget0_2 = QWidget(self)    
        #00 vertical distribution second row.Flow layout
        self.flowlaout0_2 = FlowLayout(self.widget0_2) 
        #Remove FlowLayout internal margins (including bottom margin)
        self.flowlaout0_2.setContentsMargins(0, 0, 0, 0)        
        self.flowlaout0_2.setHorizontalSpacing(15)
        self.flowlaout0_2.setVerticalSpacing(10)
        #Add the first section of controls
        self._init_flow_layout_controls()   

        #Main Content Area - Part 2 (Grid Layout)
        #00 vertically distributed third row
        self.widget0_3 = QWidget(self)    
        #========== Set the border for widget0_3 ==========
        self.widget0_3.setStyleSheet("""
            QWidget {
                border-radius: 6px;         /* 圆角 1px（可选）*/
                background-color: #1E1E1E;  /* 背景色（暗主题适配，可选）*/
                padding: 8px;  /* 内边距，避免控件贴边 */
            }
        """)
        # self._init_grid_layout_controls()

        # Q3第0行
        self.label0_3_0001 = StyledLabel('标定人',self.widget0_3)
        self.label0_3_0002 = SectionLabel('主标',self.widget0_3)
        self.textedit0_3_0004 = NewQLineEdit(self.widget0_3)    
        self.textedit0_3_0004.setMinimumWidth(150)
        self.textedit0_3_0004.setPlaceholderText("主标人：")
        self.label0_3_0006 = SectionLabel('副标',self.widget0_3)
        self.textedit0_3_0008 = NewQLineEdit(self.widget0_2)
        self.textedit0_3_0008.setMinimumWidth(150)
        self.textedit0_3_0008.setPlaceholderText("副标人：")

        # Q3第1行
        self.label0_3_0101 = StyledLabel('项目    |    次数',self.widget0_3)
        self.label0_3_0102 = StyledLabel('1',self.widget0_3)
        self.label0_3_0103 = StyledLabel('2',self.widget0_3)
        self.label0_3_0104 = StyledLabel('3',self.widget0_3)
        self.label0_3_0105 = StyledLabel('4',self.widget0_3)
        self.label0_3_0106 = StyledLabel('5',self.widget0_3)
        self.label0_3_0107 = StyledLabel('6',self.widget0_3)
        self.label0_3_0108 = StyledLabel('7',self.widget0_3)
        self.label0_3_0109 = StyledLabel('8',self.widget0_3)

        # Q3第2行  
        self.label0_3_0201 = StyledLabel('基准物质的量 g',self.widget0_3)
        self.textedit0_3_0202 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0203 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0204 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0205 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0206 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0207 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0208 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0209 = NewQLineEdit(self.widget0_3)  

        # Q3第3行  
        self.label0_3_0301 = StyledLabel('滴定液消耗体积 mL',self.widget0_3)
        self.textedit0_3_0302 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0303 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0304 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0305 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0306 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0307 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0308 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0309 = NewQLineEdit(self.widget0_3)  

        # Q3第4行  
        self.label0_3_0401 = StyledLabel('滴定管校正值 mL',self.widget0_3)
        self.textedit0_3_0402AND05 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0406AND09 = NewQLineEdit(self.widget0_3)  

        # Q3第5行  
        self.label0_3_0501 = StyledLabel('温度校正值体积 mL',self.widget0_3)
        self.textedit0_3_0502 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0503 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0504 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0505 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0506 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0507 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0508 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0509 = NewQLineEdit(self.widget0_3)  

        # Q3第6行  
        self.label0_3_0601 = StyledLabel('空白 mL',self.widget0_3)
        self.textedit0_3_0602AND05 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0606AND09 = NewQLineEdit(self.widget0_3)  

        # Q3第7行  
        self.label0_3_0701 = StyledLabel('滴定液实际体积 mL',self.widget0_3)
        self.textedit0_3_0702 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0703 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0704 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0705 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0706 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0707 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0708 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0709 = NewQLineEdit(self.widget0_3)  

        # Q3第8行  
        self.label0_3_0801 = StyledLabel('标液浓度 mol/L',self.widget0_3)
        self.textedit0_3_0802 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0803 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0804 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0805 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0806 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0807 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0808 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0809 = NewQLineEdit(self.widget0_3)  

        # Q3第9行  单人四平行浓度（mol/L）
        self.label0_3_0901 = StyledLabel('单人四平行浓度\nmol/L',self.widget0_3)
        self.textedit0_3_0902AND05 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_0906AND09 = NewQLineEdit(self.widget0_3)  


        #Q3 line 10 is relatively poor for single player
        self.label0_3_1001 = StyledLabel('单人相对极差 %',self.widget0_3)
        self.textedit0_3_1002AND05 = NewQLineEdit(self.widget0_3)  
        self.textedit0_3_1006AND09 = NewQLineEdit(self.widget0_3)  

        #Q3 line 11 The pair is relatively poor
        self.label0_3_1101 = StyledLabel('双人相对极差 %',self.widget0_3)
        self.textedit0_3_1102AND04 = NewQLineEdit(self.widget0_3)  
        self.label0_3_1105AND06 = StyledLabel('双人八平行浓度',self.widget0_3)
        self.textedit0_3_1107AND09 = NewQLineEdit(self.widget0_3) 

        #Q3 line 12 calculation formula
        self.label0_3_1201 = StyledLabel('计算公式',self.widget0_3)
        self.textedit0_3_1202AND04 = StyledLabel('默认',self.widget0_3)  
        self.label0_3_1205AND06 = StyledLabel('标液报出浓度',self.widget0_3)
        self.textedit0_3_1207AND09 = NewQLineEdit(self.widget0_3) 

        #Q3 line 13 indicate
        self.label0_3_1301 = StyledLabel('注：担任四平行标定结果相对极差≤0.15%，双人八平行标定结果相对极差≤0.18%',self.widget0_3)

        # self.remark_edit = TextEdit(self.widget0_3)
        #self.remark_edit.setPlaceholderText("Please enter remark information")
        # setFont(self.remark_edit, 13)
        
        # 占2行3列（rowSpan=2, columnSpan=3）
        self.qgridlayout0_3 = QGridLayout(self.widget0_3)
        # self.qgridlayout0_3.setSpacing(4)  
        ## Control spacing to improve aesthetics
        self.qgridlayout0_3.addWidget(self.label0_3_0001,0,0)

        #-------------------------- Key: Unified column stretch coefficient (columns 1~8) --------------------------
        #The target control occupies columns 1 to 8 (a total of 8 columns, and every 2 columns corresponds to a control). Set the same stretch factor (1) for these 8 columns.
        for col in range(1,9):  # 列索引：1,2,3,4,5,6,7,8
            #Stretch factor = 1, column width is automatically divided evenly
            self.qgridlayout0_3.setColumnStretch(col, 1)  
            #Unify the minimum column width to avoid being too narrow
            self.qgridlayout0_3.setColumnMinimumWidth(col, 60)  

        #-------------------------- Line 0 Calibration person --------------------------
        #The main bidder occupies 2 columns (starting from row 1 and column 2) and occupies 1 row and 2 columns (rowSpan=1, columnSpan=2)
        self.qgridlayout0_3.addWidget(self.label0_3_0002, 0, 1, 1, 2,Qt.AlignmentFlag.AlignCenter) 
        #The main bidder occupies 2 columns (starting from row 1 and column 3) and occupies 1 row and 2 columns (rowSpan=1, columnSpan=2)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0004, 0, 3, 1, 2,Qt.AlignmentFlag.AlignCenter) 
        #The main bidder occupies 2 columns (starting from row 1 and column 2) and occupies 1 row and 2 columns (rowSpan=1, columnSpan=2)
        self.qgridlayout0_3.addWidget(self.label0_3_0006, 0, 5, 1, 2,Qt.AlignmentFlag.AlignCenter) 
        #The main bidder occupies 2 columns (starting from row 1 and column 3) and occupies 1 row and 2 columns (rowSpan=1, columnSpan=2)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0008, 0, 7, 1, 2,Qt.AlignmentFlag.AlignCenter) 

        #-------------------------- Line 1 Number of items --------------------------
        self.qgridlayout0_3.addWidget(self.label0_3_0101,1,0,1,1)
        self.qgridlayout0_3.addWidget(self.label0_3_0102,1,1,1,1)
        self.qgridlayout0_3.addWidget(self.label0_3_0103,1,2,1,1)
        self.qgridlayout0_3.addWidget(self.label0_3_0104,1,3,1,1)
        self.qgridlayout0_3.addWidget(self.label0_3_0105,1,4,1,1)
        self.qgridlayout0_3.addWidget(self.label0_3_0106,1,5,1,1)
        self.qgridlayout0_3.addWidget(self.label0_3_0107,1,6,1,1)
        self.qgridlayout0_3.addWidget(self.label0_3_0108,1,7,1,1)
        self.qgridlayout0_3.addWidget(self.label0_3_0109,1,8,1,1)

        #-------------------------- Line 2 Amount of reference material g --------------------------
        self.qgridlayout0_3.addWidget(self.label0_3_0201,2,0,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0202,2,1,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0203,2,2,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0204,2,3,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0205,2,4,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0206,2,5,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0207,2,6,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0208,2,7,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0209,2,8,1,1)

        #-------------------------- Line 3 Titrant consumption volume --------------------------
        self.qgridlayout0_3.addWidget(self.label0_3_0301,3,0,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0302,3,1,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0303,3,2,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0304,3,3,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0305,3,4,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0306,3,5,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0307,3,6,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0308,3,7,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0309,3,8,1,1)

        #-------------------------- Line 4 Burette correction value --------------------------
        self.qgridlayout0_3.addWidget(self.label0_3_0401,4,0,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0402AND05,4,1,1,4)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0406AND09,4,5,1,4)

        #-------------------------- Line 5 Temperature Calibration Volume --------------------------
        self.qgridlayout0_3.addWidget(self.label0_3_0501,5,0,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0502,5,1,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0503,5,2,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0504,5,3,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0505,5,4,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0506,5,5,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0507,5,6,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0508,5,7,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0509,5,8,1,1)

        #-------------------------- Line 6 Blank --------------------------
        self.qgridlayout0_3.addWidget(self.label0_3_0601,6,0,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0602AND05,6,1,1,4)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0606AND09,6,5,1,4)

        #-------------------------- Line 7 Actual volume of titrant solution mL --------------------------
        self.qgridlayout0_3.addWidget(self.label0_3_0701,7,0,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0702,7,1,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0703,7,2,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0704,7,3,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0705,7,4,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0706,7,5,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0707,7,6,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0708,7,7,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0709,7,8,1,1)

        #-------------------------- Line 8 Actual volume of titrant solution mL --------------------------
        self.qgridlayout0_3.addWidget(self.label0_3_0801,8,0,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0802,8,1,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0803,8,2,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0804,8,3,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0805,8,4,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0806,8,5,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0807,8,6,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0808,8,7,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0809,8,8,1,1)

        # -------------------------- 第9行标签  单人四平行浓度（mol/L） --------------------------
        self.qgridlayout0_3.addWidget(self.label0_3_0901,9,0,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0902AND05,9,1,1,4)
        self.qgridlayout0_3.addWidget(self.textedit0_3_0906AND09,9,5,1,4)

        #-------------------------- Line 10 label Single player relative extreme % --------------------------
        self.qgridlayout0_3.addWidget(self.label0_3_1001,10,0,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_1002AND05,10,1,1,4)
        self.qgridlayout0_3.addWidget(self.textedit0_3_1006AND09,10,5,1,4)

        #----------------------------- Row 11 Label Double Relative Range % --------------------------
        self.qgridlayout0_3.addWidget(self.label0_3_1101,11,0,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_1102AND04,11,1,1,4)
        self.qgridlayout0_3.addWidget(self.label0_3_1105AND06,11,5,1,2)
        self.qgridlayout0_3.addWidget(self.textedit0_3_1107AND09,11,7,1,2)

        #-------------------------- Line 12 Label Formula --------------------------
        self.qgridlayout0_3.addWidget(self.label0_3_1201,12,0,1,1)
        self.qgridlayout0_3.addWidget(self.textedit0_3_1202AND04,12,1,1,4)
        self.qgridlayout0_3.addWidget(self.label0_3_1205AND06,12,5,1,2)
        self.qgridlayout0_3.addWidget(self.textedit0_3_1207AND09,12,7,1,2)

        #-------------------------- Line 13 Label Remarks --------------------------
        self.qgridlayout0_3.addWidget(self.label0_3_1301,13,0,1,9)


        #Function button area
        #00 vertically distributed fifth row
        self.widget0_5 = QWidget(self)    
        self.horizontalLayout0_5 = QHBoxLayout(self.widget0_5)
        self.horizontalLayout0_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout0_5.setAlignment(Qt.AlignmentFlag.AlignRight)

        #Create button (bind signal slot)
        #Query button
        self.search_btn = PushButton('查询', self.widget0_5, FIF.SEARCH) 
        #Trigger hover function
        self.search_btn.setObjectName("searchBtn")  
         #Calculate button
        self.calc_btn = PushButton('计算', self.widget0_5, FIF.CALENDAR)    
        #Trigger hover function
        self.calc_btn.setObjectName("calcBtn")  
        #save button
        self.save_btn = PushButton('保存', self.widget0_5, FIF.SAVE)        
        self.save_btn.setObjectName("saveBtn")  
        #save button
        self.default_btn = PushButton('默认', self.widget0_5, FIF.IMAGE_EXPORT)        
        self.default_btn.setObjectName("defaultBtn") 
        #clear button
        self.clear_btn = PushButton('清空', self.widget0_5, FIF.DELETE)        
        self.clear_btn.setObjectName("clearBtn") 

        #Bind button events (this is just a placeholder and can be implemented according to requirements)
        self.search_btn.clicked.connect(self.createCustomInfoBar)
        self.calc_btn.clicked.connect(self._Calculate)
        self.clear_btn.clicked.connect(self.clear_form)
        self.save_btn.clicked.connect(self.createCustomInfoBar)
        self.default_btn.clicked.connect(self._DefaultBegin) 

        #Enter calculation + keypad
        self.shortcut_enter = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        self.shortcut_enter2 = QShortcut(QKeySequence(Qt.Key.Key_Enter), self)
        self.shortcut_enter2.activated.connect(self._Calculate)
        self.shortcut_enter.activated.connect(self._Calculate)
        
        self.horizontalLayout0_5.addWidget(self.search_btn)
        self.horizontalLayout0_5.addWidget(self.calc_btn)
        self.horizontalLayout0_5.addWidget(self.save_btn)
        self.horizontalLayout0_5.addWidget(self.default_btn)
        self.horizontalLayout0_5.addWidget(self.clear_btn)
        self.horizontalLayout0_5.setSpacing(10)

        #Add all components to the main layout
        self.qvBoxlayout0.addWidget(self.widget0_1,0,Qt.AlignmentFlag.AlignHCenter)
        self.qvBoxlayout0.addWidget(self.widget0_2,0)
        self.qvBoxlayout0.addWidget(self.widget0_3,0)
        self.qvBoxlayout0.addWidget(self.widget0_5,0)
        self.qvBoxlayout0.addStretch(1)  # 添加拉伸项，使内容靠上

        #self.setWindowTitle("Standard solution original record table core")
        
        # self.label = SubtitleLabel(text, self)
        # self.hBoxLayout = QHBoxLayout(self)

        # setFont(self.label, 24)
        # self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.hBoxLayout.addWidget(self.label, 1, Qt.AlignmentFlag.AlignCenter)

        # !IMPORTANT: leave some space for title bar
        #main layout margins
        #Increase margins to improve aesthetics
        self.qvBoxlayout0.setContentsMargins(20, 32, 20, 20)  

    def _init_flow_layout_controls(self):
        """Initialize controls in fluid layout"""
        # label上边距
        labelMargins_Top = 6    

        #Standard solution concentration
        self.label0_2_01 = BodyLabel('标液浓度 mol/L',self.widget0_2)
        #Set Label top margin
        self.label0_2_01.setContentsMargins(0, labelMargins_Top, 0, 0)  

        items0_2_2 = ['标液浓度', '0.05 or less', '0.1 or 0.2', '0.5', '1']
        self.comboBox0_2_02 = ComboBox()
        self.comboBox0_2_02.addItems(items0_2_2)
        self.comboBox0_2_02.setCurrentIndex(0)

        #Standard liquid type
        items0_2_3 = ['标液种类', '水或水溶液', "盐酸", "氢氧化钠", "高锰酸钾", "硝酸银", \
                      "硫代硫酸钠", "氯化锌", "EDTA", "硫酸", "碳酸钠", "氢氧化钾-乙醇"]
        self.comboBox0_2_03 = ComboBox()
        self.comboBox0_2_03.addItems(items0_2_3)
        self.comboBox0_2_03.setCurrentIndex(0)

        # 称取质量/量取体积
        #'Measure volume mL',
        self.textedit0_2_04 = NewQLineEdit(self.widget0_2)    
        #self.textedit0_2_04.setMaximumHeight(32) #Set the maximum height
        #self.textedit0_2_04.setText("Weigh the mass g")
        self.textedit0_2_04.setPlaceholderText("称取质量 g")
        self.textedit0_2_04.setFixedWidth(95)
        #setFont(self.textedit0_2_04,13) #Set font size

        #Preparation volume
        #'Measure volume mL',
        self.textedit0_2_05 = NewQLineEdit(self.widget0_2)    
        #self.textedit0_2_05.setMaximumHeight(32) #Set the maximum height
        self.textedit0_2_05.setPlaceholderText("配制体积 L")
        self.textedit0_2_05.setFixedWidth(85)

        #-------------------------- Calibration basis (label + input box on the same line) --------------------------
        #Create a container widget and wrap the label and input box with a horizontal layout
        self.label0_2_06_And_textedit0_2_07 = QWidget(self.widget0_2)
        #Horizontal layout spacing (distance between label and input box)
        self.qhbox_2_06_AND_2_07 = QHBoxLayout(self.label0_2_06_And_textedit0_2_07)        
        self.qhbox_2_06_AND_2_07.setSpacing(6)
        #Remove the padding of the container to avoid affecting the overall layout
        self.qhbox_2_06_AND_2_07.setContentsMargins(0, 0, 0, 0)        

        self.label0_2_06 = BodyLabel('标定依据',self.label0_2_06_And_textedit0_2_07)
        #Set Label top margin
        self.label0_2_06.setContentsMargins(0, 0, 0, 0)  
        self.qhbox_2_06_AND_2_07.addWidget(self.label0_2_06)
        
        #Calibration basis input box (parent control changed to container)
        #'Measure volume mL',
        self.textedit0_2_07 = NewQLineEdit(self.label0_2_06_And_textedit0_2_07)   
        #Set maximum height
        self.textedit0_2_07.setMaximumHeight(31) 
        self.textedit0_2_07.setPlaceholderText("GB/T 601")
        self.textedit0_2_07.setFixedWidth(75)
        self.qhbox_2_06_AND_2_07.addWidget(self.textedit0_2_07)

        self.textedit0_2_08 = NewQLineEdit(self.widget0_2)    # 
        self.textedit0_2_08.setPlaceholderText("干燥条件")
        self.textedit0_2_08.setFixedWidth(75)


        #-------------------------- Calibration temperature (label + input box on the same line) --------------------------
        #Create a container widget and wrap the label and input box with a horizontal layout
        self.label0_2_09_And_textedit0_2_10 = QWidget(self.widget0_2)
        #Horizontal layout spacing (distance between label and input box)
        self.qhbox_2_09_AND_2_10 = QHBoxLayout(self.label0_2_09_And_textedit0_2_10)        
        self.qhbox_2_09_AND_2_10.setSpacing(6)
        #Remove the padding of the container to avoid affecting the overall layout
        self.qhbox_2_09_AND_2_10.setContentsMargins(0, 0, 0, 0)        

        self.label0_2_09 = BodyLabel('标定温度 ℃',self.widget0_2)
        #Set Label top margin
        self.label0_2_09.setContentsMargins(0, 0, 0, 0)  

        # 摄氏度
        self.textedit0_2_10 = NewQLineEdit(self.widget0_2)   
        #Default temperature
        self.textedit0_2_10.setPlaceholderText("℃")  
        #self.textedit0_2_10.setText("25.7") #Default temperature
        self.textedit0_2_10.setFixedWidth(47)
        self.qhbox_2_09_AND_2_10.addWidget(self.label0_2_09)
        self.qhbox_2_09_AND_2_10.addWidget(self.textedit0_2_10)



        #-------------------------- Molar mass (label + input box on the same line) --------------------------
        #Create a container widget and wrap the label and input box with a horizontal layout
        self.label0_2_11_And_textedit0_2_12 = QWidget(self.widget0_2)
        #Horizontal layout spacing (distance between label and input box)
        self.qhbox_2_11_AND_2_12 = QHBoxLayout(self.label0_2_11_And_textedit0_2_12)        
        self.qhbox_2_11_AND_2_12.setSpacing(6)
        #Remove the padding of the container to avoid affecting the overall layout
        self.qhbox_2_11_AND_2_12.setContentsMargins(0, 0, 0, 0)        

        self.label0_2_11 = BodyLabel('摩尔质量 g/mol',self.widget0_2)
        #Set Label top margin
        self.label0_2_11.setContentsMargins(0, 0, 0, 0)  
        #Calibration substance molar mass
        self.textedit0_2_12 = NewQLineEdit(self.widget0_2)   
        #Default calibration substance molar mass
        self.textedit0_2_12.setText("204.22")  
        #Default calibration substance molar mass
        self.textedit0_2_12.setPlaceholderText("204.22")  
        self.textedit0_2_12.setFixedWidth(62)

        self.qhbox_2_11_AND_2_12.addWidget(self.label0_2_11)
        self.qhbox_2_11_AND_2_12.addWidget(self.textedit0_2_12)



        #-------------------------- Configure date (label + input box on the same line) --------------------------
        #Create a container widget and wrap the label and input box with a horizontal layout
        self.label0_2_13_And_dateedit0_2_14 = QWidget(self.widget0_2)
        #Horizontal layout spacing (distance between label and input box)
        self.qhbox_2_13_AND_2_14 = QHBoxLayout(self.label0_2_13_And_dateedit0_2_14)        
        self.qhbox_2_13_AND_2_14.setSpacing(6)
        #Remove the padding of the container to avoid affecting the overall layout
        self.qhbox_2_13_AND_2_14.setContentsMargins(0, 0, 0, 0)        
        self.label0_2_13 = BodyLabel('配置日期',self.widget0_2)
        #Set Label top margin
        self.label0_2_13.setContentsMargins(0, labelMargins_Top, 0, 0)  

        self.dateedit0_2_14 = FastCalendarPicker()
        self.dateedit0_2_14.setDate(today)

        self.qhbox_2_13_AND_2_14.addWidget(self.label0_2_13)
        self.qhbox_2_13_AND_2_14.addWidget(self.dateedit0_2_14)

        # 配置人
        items0_2_16 = ['配置人','汤妹', '王志鑫', "龚金梅"]
        self.comboBox0_2_16 = ComboBox()
        #self.comboBox0_2_03.setFixedWidth(98) #Set the length of comboBox
        # print(self.comboBox0_2_03.width())
        self.comboBox0_2_16.addItems(items0_2_16)
        self.comboBox0_2_16.setCurrentIndex(0)


        #-------------------------- Validity period (label + input box on the same line) --------------------------
        #Create a container widget and wrap the label and input box with a horizontal layout
        self.label0_2_17_And_dateedit0_2_18_And_label0_2_19_And_dateedit0_2_20 = QWidget(self.widget0_2)
        #Horizontal layout spacing (distance between label and input box)
        self.qhbox_2_17_AND_2_18_AND_2_19_AND_2_20 = QHBoxLayout(self.label0_2_17_And_dateedit0_2_18_And_label0_2_19_And_dateedit0_2_20)        
        self.qhbox_2_17_AND_2_18_AND_2_19_AND_2_20.setSpacing(6)
        #Remove the padding of the container to avoid affecting the overall layout
        self.qhbox_2_17_AND_2_18_AND_2_19_AND_2_20.setContentsMargins(0, 0, 0, 0)        

        self.label0_2_17 = BodyLabel('有效期',self.widget0_2)
        #Set Label top margin
        self.label0_2_17.setContentsMargins(0, labelMargins_Top, 0, 0)  

        self.dateedit0_2_18 = FastCalendarPicker()
        self.dateedit0_2_18.setDate(today)

        self.label0_2_19 = BodyLabel('至',self.widget0_2)
        #Set Label top margin
        self.label0_2_19.setContentsMargins(0, labelMargins_Top, 0, 0)  

        self.dateedit0_2_20 = FastCalendarPicker()
        self.dateedit0_2_20.setDate(today)
        self.qhbox_2_17_AND_2_18_AND_2_19_AND_2_20.addWidget(self.label0_2_17)
        self.qhbox_2_17_AND_2_18_AND_2_19_AND_2_20.addWidget(self.dateedit0_2_18)
        self.qhbox_2_17_AND_2_18_AND_2_19_AND_2_20.addWidget(self.label0_2_19)
        self.qhbox_2_17_AND_2_18_AND_2_19_AND_2_20.addWidget(self.dateedit0_2_20)


        #-------------------------- Registration date (label + input box on the same line) --------------------------
        #Create a container widget and wrap the label and input box with a horizontal layout
        self.label0_2_21_And_dateedit0_2_22 = QWidget(self.widget0_2)
        #Horizontal layout spacing (distance between label and input box)
        self.qhbox_2_21_AND_2_22 = QHBoxLayout(self.label0_2_21_And_dateedit0_2_22)        
        self.qhbox_2_21_AND_2_22.setSpacing(6)
        #Remove the padding of the container to avoid affecting the overall layout
        self.qhbox_2_21_AND_2_22.setContentsMargins(0, 0, 0, 0)        
        self.label0_2_21 = BodyLabel('登记日期',self.widget0_2)
        #Set Label top margin
        self.label0_2_21.setContentsMargins(0, 0, 0, 0)  

        self.dateedit0_2_22 = FastCalendarPicker()
        self.dateedit0_2_22.setDate(today)

        self.qhbox_2_21_AND_2_22.addWidget(self.label0_2_21)
        self.qhbox_2_21_AND_2_22.addWidget(self.dateedit0_2_22)

        #Add controls to fluid layout #New version
        controls = [
            self.label0_2_01, self.comboBox0_2_02, self.comboBox0_2_03,
            self.textedit0_2_04, self.textedit0_2_05, self.label0_2_06_And_textedit0_2_07, 
            self.textedit0_2_08, self.label0_2_09_And_textedit0_2_10, self.label0_2_11_And_textedit0_2_12,
            self.label0_2_13_And_dateedit0_2_14, self.comboBox0_2_16,
            self.label0_2_17_And_dateedit0_2_18_And_label0_2_19_And_dateedit0_2_20, 
            self.label0_2_21_And_dateedit0_2_22
        ]
        
        for control in controls:
            self.flowlaout0_2.addWidget(control)
    

    #Get the molar mass of a standard substance
    @pyqtSlot(str)
    def _getMolarMass(self):
        nametype = self.comboBox0_2_03.currentText()
        if nametype in AppConfig.TypeTitrantList:
            substancesName = AppConfig.TypeTitrantList[nametype]['name']
            substancesMolarMass = AppConfig.TypeTitrantList[nametype]['MolarMass']
            #Set molar mass to 52.994
            self.textedit0_2_12.setText(str(substancesMolarMass))   
            # self.textedit0_2_12.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if nametype == '氯化锌':
                self.label0_2_11.setText(f"{substancesName} mol/L")
                #Measure a volume of 10 mL of zinc chloride
                self.textedit0_2_04.setText("量取体积 mL")  
                #Default calibrator EDTA concentration
                self.textedit0_2_12.setText("0.05")  
                #self.textedit0_2_12.setStyleSheet("NewQLineEdit { color: red; }") # Set font color red
                self.textedit0_2_12.setStyleSheet("""
                            NewQLineEdit {
                                color: #ff0000;        /* 字体红色（十六进制） */
                                border: 1px solid #333; 
                                background-color: #000000;  /* 背景黑色 */
                                border-radius: 4px;
                            }
                        """)
                #Set the amount of reference material in batches
                values = ['10.00'] * 8
                edits = [
                    self.textedit0_3_0202, self.textedit0_3_0203, self.textedit0_3_0204, self.textedit0_3_0205,
                    self.textedit0_3_0206, self.textedit0_3_0207, self.textedit0_3_0208, self.textedit0_3_0209
                ]
                for edit, value in zip(edits, values):
                    edit.setText(value)
            else:
                self.label0_2_11.setText(f"{substancesName} g/mol")
                self.textedit0_2_04.setText("称取质量 g")  # 不是改为称取质量
                self.textedit0_2_12.setStyleSheet("""
                            NewQLineEdit {
                                color: white;        /* 字体红色（十六进制） */
                                border: 1px solid #333; 
                                background-color: #000000;  /* 背景黑色 */
                                border-radius: 4px;
                            }
                        """)
            self._edit_setCenter()

    #Initialize startup default
    def _DefaultBegin(self):
        """Initialize startup defaults"""
        #Start default
        #Default concentration 1:4 0.5:3 0.1:2 0.05:1
        self.comboBox0_2_02.setCurrentIndex(4) 
        #self.comboBox0_2_02.setCurrentIndex(1) # #Default concentration 1:4 0.5:3 0.1:2 0.05:1
        #HCl2, NaOH3, potassium permanganate 4, silver nitrate 5, sodium thiosulfate 6
        self.comboBox0_2_03.setCurrentIndex(3) 
        #Default temperature
        self.textedit0_2_10.setText('23') 
        #self.textedit0_2_10.setText('20') #Default temperature
        # 默认基准物质的摩尔质量 g/mol
        self.textedit0_2_12.setText('204.22') 
        
        #Default value for amount of reference material
        n_values = ['7.5629', '7.5185', '7.5328', '7.5069', '7.4750', '7.4820', '7.4637', '7.4871']
        n_edits = [
            self.textedit0_3_0202, self.textedit0_3_0203, self.textedit0_3_0204, self.textedit0_3_0205,
            self.textedit0_3_0206, self.textedit0_3_0207, self.textedit0_3_0208, self.textedit0_3_0209
        ]
        for edit, value in zip(n_edits, n_values):
            edit.setText(value)
        
        #Default value of titrant consumption volume
        v_values = ['36.60', '36.36', '36.43', '36.30', '36.15', '36.20', '36.11', '36.24']
        # v_values = ['19.85', '19.84', '19.85', '19.85', '19.85', '19.85', '19.84', '19.84']
        v_edits = [
            self.textedit0_3_0302, self.textedit0_3_0303, self.textedit0_3_0304, self.textedit0_3_0305,
            self.textedit0_3_0306, self.textedit0_3_0307, self.textedit0_3_0308, self.textedit0_3_0309
        ]
        for edit, value in zip(v_edits, v_values):
            edit.setText(value)

        #Default burette correction value (mL)
        self.textedit0_3_0402AND05.setText('-0.02')  
        self.textedit0_3_0406AND09.setText('-0.02')
        #self.textedit0_3_0402AND05.setText('-0.01') #Default burette correction value (mL)
        # self.textedit0_3_0406AND09.setText('-0.01')
        #Default blank titration volume
        self.textedit0_3_0602AND05.setText('0') 
        self.textedit0_3_0606AND09.setText('0')
        self._edit_setCenter()  # 居中


    def isInt(self,INTEGER):
        """Determine whether it is an integer"""
        try:
            return Decimal(INTEGER) % 1 == 0
        except Exception as e:
            logger.error(f"判断整数失败：{str(e)}")
            return False

    def all_elements_are_valid_numbers(self,lst):
        """Determine whether all elements in the list are valid numbers (supports integers, decimals, negative numbers, and positive numbers with a + sign)
        As long as one element is an invalid number, False will be returned directly; True will be returned if all are valid."""
        #Convert to a string and remove leading and trailing spaces (if you need to strictly prohibit spaces, delete strip())
        for elem in lst:
            s = str(elem).strip()
            has_digit = has_dot = has_sign = False
            valid = True
            
            for char in s:
                if char.isdigit():
                    has_digit = True
                #The decimal point can only appear once
                elif char == '.':
                    if has_dot:
                        valid = False
                        break
                    has_dot = True
                # 符号只能在开头，且未出现过数字/小数点
                elif char in '+-':
                    if has_sign or has_digit or has_dot:
                        valid = False
                        break
                    has_sign = True
                #Containing other characters is directly invalid
                else:
                    valid = False
                    break
            #As soon as an element is invalid, False is returned immediately
            if not (valid and has_digit):   
                return False
        #All elements pass validation and return True
        return True 


    #Calculation with 2 significant figures None means the actual consumption volume has 5 significant figures ActualVolume=True
    def significant_figures(self, value, significant_figures=2,ActualVolume=None):
        """Calculation with 2 significant figures None means the actual consumption volume has 5 significant figures ActualVolume=True"""
        if value == 0:
            #For zero, return zero
            return "0.00"  
        else:
            #Decimal places
            n = significant_figures - int(math.floor(math.log10(abs(value)))) - 1
            #True value, may not contain 0
            #if value>1 or value==1: # If the solution concentration is ≥1, keep 1 more decimal place.
            #     if ActualVolume==None:
            #         n += 0
            value_no0 = round(value, n)
            #Output text based on number of decimal places
            b=(f'%.{n}f'%value_no0)
            return b
        
    ## Count the number of significant digits
    def count_figures(self, number):
        #Convert input to string and remove spaces
        number_str = str(number).strip()
        
        #Working with scientific notation
        if 'e' in number_str or 'E' in number_str:
            #Only consider the numerical part
            number_str = number_str.split('e')[0]  

        #Remove leading zeros (if floating point)
        if '.' in number_str:
            number_str = number_str.lstrip('0.')
        else:
            number_str = number_str.lstrip('0')

        #Handling zeros after decimal point
        if '.' in number_str:
            #Count significant figures
            significant_figures = len(number_str.replace('.', ''))
        else:
            significant_figures = len(number_str)

        return significant_figures
        
    #list average
    def Calculate_average(self,list_collection, NumDecimals=5, Final=False):
        begin = 0
        num = len(list_collection)
        for i in list_collection:
            #Get the number of digits after the decimal point
            begin += Decimal(i)
        NumDecimals = count_decimal_places(i)
        if Final == True:
            #Report the concentration of the standard solution, the number of decimal places is -1
            res = str(round(Decimal(begin / num),NumDecimals-1))
        else:
            res = str(round(Decimal(begin / num),NumDecimals))
        return str(res)

    #Text centering operation
    def _edit_setCenter(self):
        edit_All = [
        # 温度 \ 摩尔质量
        self.textedit0_2_10,self.textedit0_2_12,
        #Amount of reference material
        self.textedit0_3_0202,self.textedit0_3_0203,self.textedit0_3_0204,self.textedit0_3_0205,
        #Titrant consumption volume
        self.textedit0_3_0206,self.textedit0_3_0207,self.textedit0_3_0208,self.textedit0_3_0209, 
        #temperature corrected volume
        self.textedit0_3_0302,self.textedit0_3_0303,self.textedit0_3_0304,self.textedit0_3_0305,
        # ↑
        self.textedit0_3_0306,self.textedit0_3_0307,self.textedit0_3_0308,self.textedit0_3_0309,
        #Burette correction value
        self.textedit0_3_0402AND05,self.textedit0_3_0406AND09,
        # 空白
        self.textedit0_3_0602AND05,self.textedit0_3_0606AND09,
        self.textedit0_3_0509,self.textedit0_3_0502,self.textedit0_3_0502,self.textedit0_3_0503,self.textedit0_3_0504,
        #Consumption volume of fixed solution mL
        self.textedit0_3_0505,self.textedit0_3_0506,self.textedit0_3_0507,self.textedit0_3_0508,
        #Calibration concentration
        self.textedit0_3_0702,self.textedit0_3_0703,self.textedit0_3_0704,self.textedit0_3_0705,
        # ↑
        self.textedit0_3_0706,self.textedit0_3_0707,self.textedit0_3_0708,self.textedit0_3_0709, 
        #Standard solution concentration
        self.textedit0_3_0802,self.textedit0_3_0803,self.textedit0_3_0804,self.textedit0_3_0805,
        # ↑
        self.textedit0_3_0806,self.textedit0_3_0807,self.textedit0_3_0808,self.textedit0_3_0809, 
        self.textedit0_3_0902AND05,self.textedit0_3_0906AND09,self.textedit0_3_1107AND09,self.textedit0_3_1207AND09,
        #Relatively poor results for two persons
        self.textedit0_3_1002AND05,self.textedit0_3_1006AND09,self.textedit0_3_1102AND04]
        for i in edit_All:
            i.setAlignment(Qt.AlignmentFlag.AlignCenter)

    #Calculate "mark" the _Calculate method to tell Qt: this is a function that can respond to signals, such as button clicks, timer triggers, drop-down box selection changes, etc., it can be called.
    #Allow it to receive the trigger of Qt signal (Signal) and execute it
    @pyqtSlot() 
    def _Calculate(self):
        """Compute core logic"""
        #Get input
        #Standard solution concentration
        concentration_comboBox = self.comboBox0_2_02.currentText()    
        #Standard liquid type
        type_comboBox = self.comboBox0_2_03.currentText()   
        # 温度
        Temperature = self.textedit0_2_10.text()     
        #Get the amount of reference standard material
        MolarMass = self.textedit0_2_12.text()   
        #Get the amount of substance in g or ml
        n11 = self.textedit0_3_0202.text()
        n12 = self.textedit0_3_0203.text()
        n13 = self.textedit0_3_0204.text()
        n14 = self.textedit0_3_0205.text()
        n21 = self.textedit0_3_0206.text()
        n22 = self.textedit0_3_0207.text()
        n23 = self.textedit0_3_0208.text()
        n24 = self.textedit0_3_0209.text()
        ## Get titrant consumption volume
        VolumeOfTitrant11 = self.textedit0_3_0302.text()
        VolumeOfTitrant12 = self.textedit0_3_0303.text()
        VolumeOfTitrant13 = self.textedit0_3_0304.text()
        VolumeOfTitrant14 = self.textedit0_3_0305.text()
        VolumeOfTitrant21 = self.textedit0_3_0306.text()
        VolumeOfTitrant22 = self.textedit0_3_0307.text()
        VolumeOfTitrant23 = self.textedit0_3_0308.text()
        VolumeOfTitrant24 = self.textedit0_3_0309.text()
        ##burette correction value
        #Default burette correction value (mL)
        BuretteCalibration1 = self.textedit0_3_0402AND05.text()  
        BuretteCalibration2 = self.textedit0_3_0406AND09.text()

        ## Blank volume
        blank1 = self.textedit0_3_0602AND05.text()
        blank2 = self.textedit0_3_0606AND09.text()
        #Amount of reference material
        List_n = [n11,n12,n13,n14,n21,n22,n23,n24]
        #Titrant consumption volume
        List_VolumeOfTitrant = [VolumeOfTitrant11,VolumeOfTitrant12,VolumeOfTitrant13,VolumeOfTitrant14,VolumeOfTitrant21,VolumeOfTitrant22,VolumeOfTitrant23,VolumeOfTitrant24]
        #Burette correction value
        List_BuretteCalibration= [BuretteCalibration1,BuretteCalibration2]
        # 空白
        List_blank= [blank1,blank2]
        #Input validation
        try:
            #Temperature verification
            if Temperature.isdigit() == False or int(Temperature) < 5 or int(Temperature) > 36:
                self.createErrorInfoBar("温度： 在5~36℃之间的整数")
            elif not MolarMass or not self.all_elements_are_valid_numbers([MolarMass]):
                self.createErrorInfoBar("摩尔质量： 请输入有效数字")
            elif self.comboBox0_2_02.currentIndex() == 0:
                self.createErrorInfoBar("标液浓度：   请选择一个标液液浓度")
            elif self.comboBox0_2_03.currentIndex() == 0:
                self.createErrorInfoBar("标液种类：   请选择一个标液种类")
            elif self.all_elements_are_valid_numbers(List_n) == False:
                self.createErrorInfoBar("基准物质的量： 请输入一个有效数字")
            elif self.all_elements_are_valid_numbers(List_VolumeOfTitrant) == False:
                self.createErrorInfoBar("滴定液消耗体积：   输入一个有效数字")
            #Burette correction value
            elif self.all_elements_are_valid_numbers(List_BuretteCalibration) == False: 
                self.createErrorInfoBar("滴定管校正值   请输入一个有效数字")
            elif self.all_elements_are_valid_numbers(List_blank) == False:
                self.createErrorInfoBar("空白：   请输入一个有效数字")
            else:    
                if type_comboBox == '盐酸' and concentration_comboBox == '1':
                    TypeTitrant = 'HCl__1'
                elif type_comboBox == '盐酸' and concentration_comboBox == '0.5':
                    TypeTitrant = 'HCl__0_5'
                elif (type_comboBox == '氢氧化钠' or type_comboBox == '硫酸') and concentration_comboBox == '1':
                    TypeTitrant = 'SulfuricAcid__1__SodiumHydroxide__1'
                elif (type_comboBox == '氢氧化钠' or type_comboBox == '硫酸') and concentration_comboBox == '0.5':
                    TypeTitrant = 'SulfuricAcid__0_5__SodiumHydroxide__0_5'
                elif type_comboBox == '碳酸钠' and concentration_comboBox == '1':
                    TypeTitrant = 'SodiumCarbonate'
                elif type_comboBox == '氢氧化钾-乙醇' and concentration_comboBox == '0.1':
                    TypeTitrant = 'PotassiumHydroxide_ethanol__0_1'
                elif concentration_comboBox == '0.1 or 0.2':
                    TypeTitrant = 'water__0_1__0_2'
                elif concentration_comboBox == '0.05 or less':
                    TypeTitrant = 'water__0_05'
                elif concentration_comboBox == '1':
                    logger.info('该溶液在此浓度下无体积校正值')
                    self.createErrorInfoBar("请更换浓度或滴定液\n不支持该此浓度下滴定液的校正计算")
                    return None
                try:
                    dbt.cur.execute(f"SELECT {TypeTitrant} FROM VolumeCorrectionValue  WHERE temperature={Temperature}")
                    #Get the volume correction value in the db database
                    VolumeCorrectionValue = dbt.cur.fetchone()[0]
                except Exception as e:
                    dbt.conn.rollback()
                    logger.info(e)
                    return None
                finally:
                    #temperature correction value
                    temperatureCorrection11 = str(round(Decimal(VolumeCorrectionValue) * Decimal(VolumeOfTitrant11)/1000,3))
                    temperatureCorrection12 = str(round(Decimal(VolumeCorrectionValue) * Decimal(VolumeOfTitrant12)/1000,3))
                    temperatureCorrection13 = str(round(Decimal(VolumeCorrectionValue) * Decimal(VolumeOfTitrant13)/1000,3))
                    temperatureCorrection14 = str(round(Decimal(VolumeCorrectionValue) * Decimal(VolumeOfTitrant14)/1000,3))
                    temperatureCorrection21 = str(round(Decimal(VolumeCorrectionValue) * Decimal(VolumeOfTitrant21)/1000,3))
                    temperatureCorrection22 = str(round(Decimal(VolumeCorrectionValue) * Decimal(VolumeOfTitrant22)/1000,3))
                    temperatureCorrection23 = str(round(Decimal(VolumeCorrectionValue) * Decimal(VolumeOfTitrant23)/1000,3))
                    temperatureCorrection24 = str(round(Decimal(VolumeCorrectionValue) * Decimal(VolumeOfTitrant24)/1000,3))

                    #Count the number of significant figures
                    ## list of valid digits
                    count_figures_List = [n11,n12,n13,n14,n21,n22,n23,n24]  
                    #Count the significant figures of the amounts of all substances, and use the maximum value as the number of significant figures of the volume consumed by the titrant.
                    all_count_figures = [self.count_figures(float(X_num)) for X_num in count_figures_List]  
                    all_count_figures.sort(reverse=True) # 排序从大到小
                    max_count_figures = all_count_figures[0]

                    #Calculation of titrant reagent consumption volume True means the actual consumption volume has 5 significant figures.
                    ActualVolume11 = self.significant_figures(float(VolumeOfTitrant11) + float(BuretteCalibration1) + float(temperatureCorrection11) + float(blank1),5,True)
                    ActualVolume12 = self.significant_figures(float(VolumeOfTitrant12) + float(BuretteCalibration1) + float(temperatureCorrection12) + float(blank1),5,True)
                    ActualVolume13 = self.significant_figures(float(VolumeOfTitrant13) + float(BuretteCalibration1) + float(temperatureCorrection13) + float(blank1),5,True)
                    ActualVolume14 = self.significant_figures(float(VolumeOfTitrant14) + float(BuretteCalibration1) + float(temperatureCorrection14) + float(blank1),5,True)
                    ActualVolume21 = self.significant_figures(float(VolumeOfTitrant21) + float(BuretteCalibration2) + float(temperatureCorrection21) + float(blank2),5,True)
                    ActualVolume22 = self.significant_figures(float(VolumeOfTitrant22) + float(BuretteCalibration2) + float(temperatureCorrection22) + float(blank2),5,True)
                    ActualVolume23 = self.significant_figures(float(VolumeOfTitrant23) + float(BuretteCalibration2) + float(temperatureCorrection23) + float(blank2),5,True)
                    ActualVolume24 = self.significant_figures(float(VolumeOfTitrant24) + float(BuretteCalibration2) + float(temperatureCorrection24) + float(blank2),5,True)

                    #Calculation of calibration concentration
                    #Zinc chloride is calculated separately
                    if self.comboBox0_2_03.currentText() == '氯化锌': 
                        CalibrationConcentration11 = self.significant_figures(float(n11) * float(MolarMass) / float(ActualVolume11),5)
                        CalibrationConcentration12 = self.significant_figures(float(n12) * float(MolarMass) / float(ActualVolume12),5)
                        CalibrationConcentration13 = self.significant_figures(float(n13) * float(MolarMass) / float(ActualVolume13),5)
                        CalibrationConcentration14 = self.significant_figures(float(n14) * float(MolarMass) / float(ActualVolume14),5)
                        CalibrationConcentration21 = self.significant_figures(float(n21) * float(MolarMass) / float(ActualVolume21),5)
                        CalibrationConcentration22 = self.significant_figures(float(n22) * float(MolarMass) / float(ActualVolume22),5)
                        CalibrationConcentration23 = self.significant_figures(float(n23) * float(MolarMass) / float(ActualVolume23),5)
                        CalibrationConcentration24 = self.significant_figures(float(n24) * float(MolarMass) / float(ActualVolume24),5)
                    else:
                        CalibrationConcentration11 = self.significant_figures(float(n11) * 1000 / float(MolarMass) / float(ActualVolume11),5)
                        CalibrationConcentration12 = self.significant_figures(float(n12) * 1000 / float(MolarMass) / float(ActualVolume12),5)
                        CalibrationConcentration13 = self.significant_figures(float(n13) * 1000 / float(MolarMass) / float(ActualVolume13),5)
                        CalibrationConcentration14 = self.significant_figures(float(n14) * 1000 / float(MolarMass) / float(ActualVolume14),5)
                        CalibrationConcentration21 = self.significant_figures(float(n21) * 1000 / float(MolarMass) / float(ActualVolume21),5)
                        CalibrationConcentration22 = self.significant_figures(float(n22) * 1000 / float(MolarMass) / float(ActualVolume22),5)
                        CalibrationConcentration23 = self.significant_figures(float(n23) * 1000 / float(MolarMass) / float(ActualVolume23),5)
                        CalibrationConcentration24 = self.significant_figures(float(n24) * 1000 / float(MolarMass) / float(ActualVolume24),5)
                    #Calculate the concentration of standard solution in four parallel lines for one person
                    SingleParallel1 = self.Calculate_average([CalibrationConcentration11, CalibrationConcentration12, CalibrationConcentration13, CalibrationConcentration14])
                    SingleParallel2 = self.Calculate_average([CalibrationConcentration21, CalibrationConcentration22, CalibrationConcentration23, CalibrationConcentration24])

                    #Calculate the concentration of standard solution for two people and eight parallels
                    DoubleParallel = self.Calculate_average([CalibrationConcentration11, CalibrationConcentration12, CalibrationConcentration13, CalibrationConcentration14, \
                                                            CalibrationConcentration21, CalibrationConcentration22, CalibrationConcentration23, CalibrationConcentration24])
                    #Calculate the reported concentration of the standard solution
                    Report = self.Calculate_average([CalibrationConcentration11, CalibrationConcentration12, CalibrationConcentration13, CalibrationConcentration14, \
                                                    CalibrationConcentration21, CalibrationConcentration22, CalibrationConcentration23, CalibrationConcentration24], Final=True)    
                    
                    #Get the number of digits after the decimal point
                    Report_num_places = count_decimal_places(Report)
                    #Can retain the last digit of 0
                    Report = str(round(Decimal(Report),Report_num_places)) 
                    # Report = str(round(Report,int(Report_num_places)-2))

                    #Calculate calibration concentration list
                    ParallelConcentration1 = [CalibrationConcentration11,CalibrationConcentration12,CalibrationConcentration13,CalibrationConcentration14]
                    ParallelConcentration2 = [CalibrationConcentration21,CalibrationConcentration22,CalibrationConcentration23,CalibrationConcentration24]
                    #Calibration concentration list sorting
                    ParallelConcentration1.sort(reverse=True)
                    ParallelConcentration2.sort(reverse=True)
                    # 主/副标人 相对极差%
                    relativeRange1 = '{:.2%}'.format((float(ParallelConcentration1[0]) - float(ParallelConcentration1[-1])) / float(SingleParallel1))
                    relativeRange2 = '{:.2%}'.format((float(ParallelConcentration2[0]) - float(ParallelConcentration2[-1])) / float(SingleParallel2))
                    #Double Eight Parallel Relative Range %
                    ParallelConcentration = []
                    ParallelConcentration.extend(ParallelConcentration1)
                    ParallelConcentration.extend(ParallelConcentration2)
                    ParallelConcentration.sort(reverse=True)
                    relativeRange = '{:.2%}'.format((float(ParallelConcentration[0]) - float(ParallelConcentration[-1])) / float(DoubleParallel))


                    #Temperature corrected volume mL Q3 line 7
                    self.textedit0_3_0502.setText(temperatureCorrection11)
                    self.textedit0_3_0503.setText(temperatureCorrection12)
                    self.textedit0_3_0504.setText(temperatureCorrection13)
                    self.textedit0_3_0505.setText(temperatureCorrection14)
                    self.textedit0_3_0506.setText(temperatureCorrection21)
                    self.textedit0_3_0507.setText(temperatureCorrection22)
                    self.textedit0_3_0508.setText(temperatureCorrection23)
                    self.textedit0_3_0509.setText(temperatureCorrection24)

                    #Set titrant consumption volume mL Q3 line 7
                    self.textedit0_3_0702.setText(ActualVolume11)
                    self.textedit0_3_0703.setText(ActualVolume12)
                    self.textedit0_3_0704.setText(ActualVolume13)
                    self.textedit0_3_0705.setText(ActualVolume14)
                    self.textedit0_3_0706.setText(ActualVolume21)
                    self.textedit0_3_0707.setText(ActualVolume22)
                    self.textedit0_3_0708.setText(ActualVolume23)
                    self.textedit0_3_0709.setText(ActualVolume24)

                    #Set calibration concentration
                    self.textedit0_3_0802.setText(CalibrationConcentration11)
                    self.textedit0_3_0803.setText(CalibrationConcentration12)
                    self.textedit0_3_0804.setText(CalibrationConcentration13)
                    self.textedit0_3_0805.setText(CalibrationConcentration14)
                    self.textedit0_3_0806.setText(CalibrationConcentration21)
                    self.textedit0_3_0807.setText(CalibrationConcentration22)
                    self.textedit0_3_0808.setText(CalibrationConcentration23)
                    self.textedit0_3_0809.setText(CalibrationConcentration24)

                    #Setting up single player four parallel concentration
                    #Main marker parallel standard solution concentration
                    self.textedit0_3_0902AND05.setText(SingleParallel1) 
                    #Sub-standardizer parallel standard solution concentration
                    self.textedit0_3_0906AND09.setText(SingleParallel2) 
                    #Double eight parallel standard solution concentration
                    self.textedit0_3_1107AND09.setText(DoubleParallel) 
                    #Report the standard solution concentration
                    self.textedit0_3_1207AND09.setText(Report) 


                    #Setting Single player relative range %
                    self.textedit0_3_1002AND05.setText(relativeRange1)
                    self.textedit0_3_1006AND09.setText(relativeRange2)
                    #Relative extreme poor% for two persons
                    self.textedit0_3_1102AND04.setText(relativeRange) 

                    self.createSuccessInfoBar("计算完成！")
                    # self._edit_setCenter()

        except Exception as e:
            logger.error(f"计算过程出错：{str(e)}", exc_info=True)
            self.createErrorInfoBar(f"请检查 VolumeCorrectionValue.db 是否存在或失效 \nError:    {str(e)}")


    def clear_form(self):
        """Clear all input box contents"""
        try:
            #Clear the input box in the flow layout
            flow_edits = [
                self.textedit0_2_04, self.textedit0_2_05, self.textedit0_2_07,
                self.textedit0_2_08, self.textedit0_2_10, self.textedit0_2_12
            ]
            for edit in flow_edits:
                edit.clear()
            
            #Clear the input box in the grid layout
            for edit in self.findChildren(NewQLineEdit):
                if edit not in flow_edits:
                    edit.clear()
            
            #Reset drop-down box
            self.comboBox0_2_02.setCurrentIndex(0)
            self.comboBox0_2_03.setCurrentIndex(0)
            self.comboBox0_2_16.setCurrentIndex(0)
            
            #Reset date picker
            self.dateedit0_2_14.setDate(today)
            self.dateedit0_2_18.setDate(today)
            self.dateedit0_2_20.setDate(today)
            self.dateedit0_2_22.setDate(today)

            self.createSuccessInfoBar("表单已清空")
            # 居中
            self._edit_setCenter() 
        except Exception as e:
            logger.error(f"清空表单失败：{str(e)}")
            self.createErrorInfoBar(f"清空失败：{str(e)}")


class Window(SplitFluentWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        # create sub interface
        self.homeInterface = MainWidget('Standard Solution Original Record Review', self)
        self.musicInterface = Widget('Music Interface 开发中...', self)
        self.videoInterface = Widget('Video Interface 开发中...', self)
        self.settingInterface = Widget('Setting Interface 开发中...', self)
        self.albumInterface = Widget('Album Interface 开发中...', self)
        self.initNavigation()
        self.initWindow()

    #Initialize navigation
    def initNavigation(self):
        #IconHOME NameHOME
        self.addSubInterface(self.homeInterface, FIF.HOME, '标准溶液计算')  
        #...Other navigation items (unchanged)...

        if not os.path.exists(avatar_path):
            logger.info(f"头像文件不存在：{avatar_path}，使用默认图标")
            avatar_widget = NavigationAvatarWidget(APP_AUTHOR, ':/qfluentwidgets/images/logo.png')
        else:
            avatar_widget = NavigationAvatarWidget(APP_AUTHOR, avatar_path)

        self.navigationInterface.addWidget(
            routeKey='avatar',
            #Use the spliced ​​path instead
            widget=avatar_widget,  
            onClick=self.showMessageBox,
            position=NavigationItemPosition.BOTTOM,
        )

        self.addSubInterface(self.musicInterface, FIF.MUSIC, '...开发中...')
        self.addSubInterface(self.videoInterface, FIF.VIDEO, '...开发中...')
        # 分割线
        self.navigationInterface.addSeparator() 

        self.addSubInterface(self.albumInterface, FIF.ALBUM, '...开发中...', NavigationItemPosition.SCROLL)

        #add custom widget to bottom Add custom widget to bottom
        self.navigationInterface.addWidget(
            routeKey='avatar',
            # 图片
            widget=NavigationAvatarWidget(APP_AUTHOR, 'resource/deathNote.png'),    
            onClick=self.showMessageBox,
            position=NavigationItemPosition.BOTTOM,
        )
        # 设定
        self.addSubInterface(self.settingInterface, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM) 

        # NOTE: enable acrylic effect
        # self.navigationInterface.setAcrylicEnabled(True)

    def initWindow(self):
        """initialization window"""
        self.resize(*AppConfig.WINDOW_SIZE)
        #Check if the file exists (optional, for debugging)
        if not os.path.exists(icon_path):
            print(f"警告：图标文件不存在！路径：{icon_path}")
            #Change to another application icon
            self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))   
        else:
            #form icon
            self.setWindowIcon(QIcon(icon_path))  
        self.setWindowTitle(AppConfig.WINDOW_TITLE)  # 
        #Available area geometry information for the home screen
        desktop = QApplication.screens()[0].availableGeometry() 
        w, h = desktop.width(), desktop.height()
        #Move to center
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)  

    #Custom controls
    def showMessageBox(self):
        w = MessageBox(
                    '关于软件',
                    f'''{APP_NAME}

             {APP_VERSION}

            Developer: {APP_AUTHOR}
            Copyright {APP_COPYRIGHT}

            This software is used for laboratory standard solution data review,
            Automatic calculation and quality control.
            
            Support the author 🥰

            If this project helps you, you may consider asking the author to drink a bottle of happy water🥤''',
            self
        )
        w.cancelButton.setText('强力支持')
        w.yesButton.setText('下次一定')

        if w.exec() == False:
            QDesktopServices.openUrl(QUrl("https://github.com/weigefenxiang"))


if __name__ == '__main__':
    dbt = dbtool(dbpath)
    setTheme(Theme.DARK)
    app=QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec())