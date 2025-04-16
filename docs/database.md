# Tortoise ORM 和 PostgreSQL 数据库配置指南

本项目使用 Tortoise ORM 作为ORM框架，PostgreSQL 作为数据库。以下是使用说明和配置指南。

## 配置步骤

### 1. 安装依赖

项目已经在 `requirements.txt` 中包含了必要的依赖：

```bash
pip install -r requirements.txt
```

主要相关依赖:
- tortoise-orm: Tortoise ORM 框架
- asyncpg: PostgreSQL 异步驱动
- aerich: 数据库迁移工具

### 2. 配置数据库连接

在 `.env` 文件中配置数据库连接信息：

```
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=llamakb
```

根据不同环境，可以在 `.env.development`, `.env.testing`, `.env.production` 文件中配置不同的数据库连接信息。

### 3. 创建 PostgreSQL 数据库

在 PostgreSQL 中创建数据库：

```sql
CREATE DATABASE llamakb;
```

对于开发环境：

```sql
CREATE DATABASE llamakb_dev;
```

### 4. 初始化数据库

运行初始化脚本：

```bash
python init_db.py
```

### 5. 使用 Aerich 进行数据库迁移

初始化 Aerich：

```bash
aerich init -t app.core.database.TORTOISE_ORM
```

创建初始迁移：

```bash
aerich init-db
```

每次模型变更后，创建新的迁移：

```bash
aerich migrate --name add_new_field
```

应用迁移：

```bash
aerich upgrade
```

## 模型定义

在 `app/models/models.py` 中定义数据模型。基本示例：

```python
from tortoise import fields
from tortoise.models import Model

class BaseModel(Model):
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True

class Document(BaseModel):
    title = fields.CharField(max_length=255)
    content = fields.TextField()
    
    class Meta:
        table = "documents"
```

## 使用模型

在服务层中使用模型：

```python
# 创建
document = await Document.create(title="示例文档", content="这是内容")

# 查询
documents = await Document.all()
document = await Document.filter(id=1).first()

# 更新
document.title = "新标题"
await document.save()

# 删除
await document.delete()
```

## 关系查询

Tortoise ORM 支持关系查询：

```python
# 定义关系
class Category(BaseModel):
    name = fields.CharField(max_length=50)
    
class Article(BaseModel):
    title = fields.CharField(max_length=255)
    category = fields.ForeignKeyField("models.Category", related_name="articles")
    
# 使用关系查询
category = await Category.filter(id=1).prefetch_related("articles").first()
articles = category.articles

# 反向查询
article = await Article.filter(id=1).select_related("category").first()
category = article.category
```

## 事务支持

使用事务确保数据一致性：

```python
async with in_transaction() as conn:
    category = await Category.create(name="新分类", using_db=conn)
    await Article.create(title="新文章", category=category, using_db=conn)
```

更多详细使用方法请参考 [Tortoise ORM 文档](https://tortoise-orm.readthedocs.io/)。 