# 标准溶液计算审核系统

![Python](https://img.shields.io/badge/Python-3.12-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue)
![GPL-3.0](https://img.shields.io/badge/GPL--3.0-red)

一款用于实验室标准溶液标定、计算与审核的软件。

支持温度校正、滴定管校正、单人四平行、双人八平行及相对极差自动计算。

![](https://img.weigeshare.cc.cd/img/002.StandardSolution_Review_System_Demo_GIF.gif)

即可计算

## 功能特点

✅ 温度校正计算
✅ 滴定管校正值修正
✅ 标液浓度自动计算

✅ 单人四平行计算
✅ 双人八平行计算
✅ 相对极差计算 
✅ 标液报出浓度计算

## 支持的标准溶液

- 盐酸、氢氧化钠、硫酸、高锰酸钾、硝酸银、硫代硫酸钠、乙二胺四乙酸（EDTA）、氯化锌、氢氧化钾-乙醇、碳酸钠等

- HCl、NaOH、H₂SO₄、KMnO₄、AgNO₃、Na₂S₂O₃、EDTA、ZnCl₂、KOH-Ethanol、Na₂CO₃、Custom Molar Mass (g/mol)

***自定义**

## 运行方式

### 发布版

下载 并 运行 [exe](https://github.com/weigefenxiang/StandardSolutionReviewSystem/releases)：

```text
StandardSolution_ReviewSystem.exe
```

## 源码运行

### 开发环境

- Windows 11
- Python 3.12
- PyQt6
- QFluentWidgets
- SQLite
- Nuitka（用于打包）

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

```bash
python Flu_Main.py
```

## 作者

Wei.G

GitHub：https://github.com/weigefenxiang

## 开源协议

本项目采用 GPL-3.0 License 开源。

使用、修改和分发本项目时，请遵守 GPL-3.0 许可证要求。

## 第三方开源组件

本项目使用了以下开源项目：

- Python
- PyQt6
- QFluentWidgets
- SQLite
- Nuitka

感谢所有开源项目开发者的贡献。