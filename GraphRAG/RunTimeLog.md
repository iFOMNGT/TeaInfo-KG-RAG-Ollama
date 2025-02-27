# GraphRAG茶叶运行记录
## 生成项目目录（init）
使用命令行，生成项目目录
```shell
python -m graphrag init --root ~/GraphRAG
```

## config配置更改（settings.yaml）
在生成的工程文件目录下，修改settings配置
### LLM部分
- 修改``api_base``参数为ollama端口（v1）
- 修改``max_tokens``为16000（默认4000）
- 修改``request_timeout``为360秒（默认180）
- 修改``max_retries``为20（默认为10）
- 修改``concurrent_requests``为3（默认为25）

### embedding-LLM
- 修改``api_base``为ollama端口（api）

### 数据保存目录
- 数据目录以序列号进行命名（1st、2nd、3rd），与每一次更新迭代相对应

### logs日志保存
- 日志文件与最终生成的数据一同保存在同一目录下

### 实体提取部分（entity_extraction）
- 修改实体类型（entity_types）为
```
[加工方式, 茶种类, 制茶工艺, 茶叶特性, 选购常识, 茶叶产地, 茶树害虫, 茶树病害, 防治方法, 气候类型, 功效, 医疗价值, 茶文化, 习俗, 人物, 事件, 地点]
```

### 摘要描述部分（summarize_descriptions）
- 修改``max_length``为800（默认为500）

### 社区报告部分（community_reports）
- 修改``max_length``为7000（qwen2.5的最大输出长度是8k）（默认2000）
- 修改``max_input_length``为25600（qwen2.5的最大上下文长度是128k）（默认8000）

## 提示词自动调优(prompt tuning)
在正式运行GraphRAG前，先使用自带的Auto Prompt Tuning功能将提示词作初步调整。在生成提示此后，增加一些特殊说明，将符号含义告知（==、--、~~与空行）。
### 提示词参数指定
- 首先指定选择**文档数量**参数``--selection-method``选择``auto`` 。
    >- random: Select text units r和omly. This is the default and recommended option.
    >- top: Select the head n text units.
    >- all: Use all text units for the generation. Use only with small datasets; this option is not usually recommended.
    >- auto: Embed text units in a lower-dimensional space and select the k nearest neighbors to the centroid. This is useful when you have a large dataset 和 want to select a representative sample.
- ``--language``**实体提取语言**参数选择``Chinese``，虽然文档里有说会自动识别，但这边依旧选择手动指明。  
- ``--min-examples-required``**生成样例数量**的参数填写``18``个，目前不知道生成样例过多是否会对最终的实体提取起反作用，但目前想提高模板的多样性，故填写18个。
- ``--discover-entity-types``，提高实体提取范围与提取类型的准确性，以下是官方文档原文解释
    > Use untyped entity extraction generation. We recommend using this when your data covers a lot of topics or it is highly randomized.

最终可选定提示词命令为
```shell
python -m graphrag prompt-tune --root ~/GraphRAG --selection-method all --language Chinese --discover-entity-types --output ~/GraphRAG/prompts
```

## 正式运行GraphRAG(index)
正式一步一步的运行所有数据
1. 首先将 **工业流程** 的数据读取
2. 增量 **茶树病害** 的数据
3. 增量 **茶树害虫** 的数据
4. 增量 **制茶技艺** 的数据