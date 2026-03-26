# bip_project

ВНИМАНИЕ! Установите зависимости - желательно, в виртуальном окуржении для отсутствия конфликтов версий

```
python -m venv venv
source venv/bin/activate 
```

```
pip install -r requirements.txt
```

Для последующих коммитов при изменениях в модели требуется git lfs (не который Linux From Scratch :D, а который Large File Storage) - так как модель большая

Если работаете на Linux, проще установить проще всего через HomeBrew
```
brew install git-lfs
git lfs install
```

Далее, включаем отслеживание файла модели:

```
git lfs track "*.safetensors"
```

Если вдругг сделали коммит до настройки git lfs, потребуется команда

```
git lfs migrate import --include="*.safetensors" --everything
```

Запуште изменения:

```
git push --force origin ai-branch
```

---

Смотреть внимательно название модели!! И ее папку!!!
MODEL_NAME = "xlm-roberta-base"
DEFAULT_MODEL_PATH = "D:\\vas\\БИП\\bip_project\\test_ml\\final_model_test"