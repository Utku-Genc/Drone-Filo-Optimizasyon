
# 🚁 DRONE-FİLO-OPTİMİZASYON

**Teslimatları Akıllı Planla, Lojistiği Yeniden Şekillendir!**

![last-commit](https://img.shields.io/github/last-commit/Utku-Genc/Drone-Filo-Optimizasyon?style=flat&logo=git&color=0080ff)
![repo-top-language](https://img.shields.io/github/languages/top/Utku-Genc/Drone-Filo-Optimizasyon?style=flat&color=0080ff)
![language-count](https://img.shields.io/github/languages/count/Utku-Genc/Drone-Filo-Optimizasyon?style=flat&color=0080ff)
![python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat&logo=python&logoColor=white)

---

## 📌 Proje Özeti

Bu proje, çok sayıda drone’un çok sayıda teslimat görevini belirli kısıtlar altında en verimli şekilde gerçekleştirmesini sağlayan bir **filo optimizasyon yazılımıdır**.

### 🚀 Temel Özellikler:
- 🧠 **A\*** ve **Genetik Algoritmalar** ile rota optimizasyonu
- 📦 **Kısıt Tatmin Problemi (CSP)** ile görev-drone eşleşmesi
- 📍 **Graf Tabanlı Yapı** ile konumlar ve yasak bölgeler modellenir
- 🧪 **Simülasyon Modülü** ile teslimat operasyonları test edilir
- 📊 **Görselleştirme Araçları** ile rota ve görev analizleri sunulur

---

## 🗂️ Proje Yapısı

```bash
Drone-Filo-Optimizasyon/
│
├── main.py                # Giriş noktası
├── models/                # Temel veri sınıfları (Drone, Paket, Konum)
├── algorithms/            # A*, Genetik Algoritma, CSP çözücü
├── simulation/            # Simülasyon yöneticisi
├── utils/                 # Yardımcı fonksiyonlar & görselleştirme
├── sample_data/           # Sabit örnek veriler
└── requirements.txt       # Gerekli bağımlılıklar
````

---

## ⚙️ Gereksinimler

* Python 3.10 veya üzeri
* Gerekli kütüphaneler:

  * matplotlib
  * numpy
  * networkx
  * pytest (isteğe bağlı)

---

## 🔧 Kurulum
### 1. Projeyi klonlayın:

```bash
git clone https://github.com/Utku-Genc/Drone-Filo-Optimizasyon
cd Drone-Filo-Optimizasyon
```

### 2. Gerekli bağımlılıkları yükleyin:

```bash
pip install matplotlib numpy networkx pytest
```

---

## ▶️ Kullanım

> `$calistiralacak_klasor` yerine çalıştırmak istediğiniz klasör adını yazınız.

```bash
python $calistiralacak_klasor/main.py
```

---

## 📈 Örnek Çıktılar

Aşağıda proje çalıştırıldığında elde edilen bazı görseller yer almaktadır:

### 📌 Örnek 1: Drone Rota Görselleştirmesi
![Figure_1](https://github.com/user-attachments/assets/1a809b3e-c017-4c94-a3ff-592fd1c2bb1e)
![Figure_2](https://github.com/user-attachments/assets/8cf5d2fe-f67c-4a92-9d3e-d573c37b40a6)


### 📌 Örnek 2: Kalkış Noktasında Teslim Almalı Drone Rota Görselleştirmesi

![Figure_3](https://github.com/user-attachments/assets/abc3096f-1f04-4781-a65a-f9d51e4d15d4)

---

## 📚 Lisans

Bu proje, **Kocaeli Üniversitesi - Bilişim Sistemleri Mühendisliği** kapsamında **Yazılım Geliştirme Lab. II** dersi için geliştirilmiştir.

---

🔼 [Başa Dön](#drone-filo-optimizasyon)

---
English
---

# 🚁 DRONE-FLEET-OPTIMIZATION

**Plan Deliveries Smartly, Reshape Logistics!**

![last-commit](https://img.shields.io/github/last-commit/Utku-Genc/Drone-Filo-Optimizasyon?style=flat&logo=git&color=0080ff)
![repo-top-language](https://img.shields.io/github/languages/top/Utku-Genc/Drone-Filo-Optimizasyon?style=flat&color=0080ff)
![language-count](https://img.shields.io/github/languages/count/Utku-Genc/Drone-Filo-Optimizasyon?style=flat&color=0080ff)
![python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat&logo=python&logoColor=white)

---

## 📌 Project Summary

This project is a **fleet optimization software** that enables multiple drones to perform delivery tasks under various constraints in the most efficient way.

### 🚀 Key Features:
- 🧠 Route optimization using **A\*** and **Genetic Algorithms**
- 📦 Task-to-drone assignment via **Constraint Satisfaction Problem (CSP)**
- 📍 Location and no-fly zones modeled with **Graph-based Structures**
- 🧪 **Simulation Module** for testing operational scenarios
- 📊 **Visualization Tools** for analyzing drone routes and assignments

---

## 🗂️ Project Structure

```bash
Drone-Filo-Optimizasyon/
│
├── main.py                # Entry point
├── models/                # Core data classes (Drone, Package, Location)
├── algorithms/            # A*, Genetic Algorithm, CSP solver
├── simulation/            # Simulation manager
├── utils/                 # Helper functions & visualization
├── sample_data/           # Fixed sample datasets
└── requirements.txt       # Python dependencies
````

---

## ⚙️ Requirements

* Python 3.10+
* Required libraries:

  * matplotlib
  * numpy
  * networkx
  * pytest (optional)

---

## 🔧 Installation
### 1. Clone the repository:

```bash
git clone https://github.com/Utku-Genc/Drone-Filo-Optimizasyon
cd Drone-Filo-Optimizasyon
````

### 2. Install required dependencies:

```bash
pip install matplotlib numpy networkx pytest
```

---

## ▶️ Usage

> Replace `$target_folder` with the folder you want to run.

```bash
python $target_folder/main.py
```
---

## 📈 Sample Outputs

Below are some sample outputs generated during simulation:

### 📌 Example 1: Drone Route Visualization


![Figure_1](https://github.com/user-attachments/assets/1a809b3e-c017-4c94-a3ff-592fd1c2bb1e)  
![Figure_2](https://github.com/user-attachments/assets/8cf5d2fe-f67c-4a92-9d3e-d573c37b40a6)

### 📌Example 2: Drone Route with Pickup at Departure Point

![Figure_3](https://github.com/user-attachments/assets/abc3096f-1f04-4781-a65a-f9d51e4d15d4)

---

## 📚 License

This project was developed for the **Software Development Lab II** course at **Kocaeli University, Department of Information Systems Engineering**.

---

🔼 [Back to Top](#drone-fleet-optimization)


