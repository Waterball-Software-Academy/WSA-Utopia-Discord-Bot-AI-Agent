# 貢獻指引

## 架構：Package by Feature, then package by layer

本專案遵從 "Package by Feature, then package by layer" 架構，第一層我們先以「功能」來區分 Package，好比：「新成員降落體驗 (landingx)」 獨立為一包、「技術分享 (speech)」獨立為另一包。

每一包裡面再 "Package by Layer"，將該功能項目分成「應用 (app)/測試 (test)」，並且應用包中繼續依循 "Package by layer" 做分層。

## 有哪些 Feature？

本專案 Feature 的顆粒度類似於 "Epic"，其顆粒度為「一組相關的功能和使用案例」，而這一組功能能共同創造某一面向的價值。

如，本專案將所有和「新成員加入之後所經歷的各種連續體驗」，稱之為「降落體驗 (landing experience)」——縮寫為 landingx。那專案最外層就會有一包 "landingx" Feature，以此類推。

以下為本專案所有 Feature Package 的簡單介紹：
1. landingx (降落體驗)：新成員加入之後所經歷的各種連續體驗
2. speech（技術分享）：鼓勵學院工程師透過自在的技術分享，藉由大量的「輸入」及「輸出」的過程中做到高效率的「費曼學習」，同時也造福了愛吃瓜的社群朋友們。
3. empower（創造培力）：藉由自動化技術，允許並放大所有社群成員能自組織舉辦活動，從活動中獲取自己想要的價值的一系列基礎建設。
