要将基于LLM的应用程序应用在生产环境，需要思考的一些点：

## MLOps流程：



### 评价体系

设置对RAG的评价指标，以快速原型作为baseline，通过评价指标评估可用程度，以这为目标进行相应优化

建立用户反馈机制，增加这种评价指标



### 开发流程管理

手动原型开发-> 机器学习与LLM管道自动化 -> CI/CD管道自动化

实验，分析任务范围内可用数据EDA，质量数据集，ML模型训练与验证，Benchmark超参数管理，自动化工作流程， A/B测试，上线部署，反馈，服务和监控



### 数据获取

异构数据源的管理与接入。PDF uploads, YouTube videos, web scraping, third-party APIs, and so on

弹性与异常的处理



### 三方API的弹性问题



例如OpenAI的服务挂了咋整？例如OpenAI API的访问限制问题如何处理，等等



对于三方API更新的弹性处理能力，例如OpenAI的API升级导致大量break-change问题等等



## 业务考虑：

- 合并现有业务
- 要构建具有高可用性、精确度和功能的虚拟助手，如实时更新价格和库存，实时收集用户反馈和隐含偏好的推荐系统，用户跟踪和满意度监测，以保持用户和业务满意，等等。
- 24/7 准确与快速相应



## Cost 成本评估体系

监控Cost

Can you compare the costs of two vendors or even self-hosting?



## 企业级API_KEY管理



## 安全性

sensitive information about the company or other users? 

对于数据的合规性问题考虑PII rules 还有其他 regulations



## 质量与用户满意度

你能跟踪用户提示和聊天回复吗?拥有跟踪系统对于保证和监控系统的质量至关重要。然而，用户的隐私权也需要得到保障。构建一个反馈系统，帮助您快速修复RAG中的问题，同时又符合用户隐私，这是一项非常复杂的任务。

### 用户的易用性

比如是针对常用场景给出Prompt模板，或者像midjourny用反向工程，还是说直接到下一步AGI。因为我感觉商用的话，业务人员如果不熟悉prompt使用起来就不能发挥模型的最大优势