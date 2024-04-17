from layoutparser.models import Detectron2LayoutModel, detectron2
import requests
import copy
import os


class ExtractLayout(Detectron2LayoutModel):

    def __init__(self,
                 config_path: str = 'lp://TableBank/faster_rcnn_R_101_FPN_3x/config',
                 *args,
                 **kwargs
                 ):
        """
        The following modified __init__ is to solve this issue:
                 https://github.com/Layout-Parser/layout-parser/issues/168

        :param config_path: A path to the config file
        """

        config_path_split = config_path.split('/')
        dataset_name = config_path_split[-3]
        model_name = config_path_split[-2]

        model_url = Detectron2LayoutModel.MODEL_CATALOG[dataset_name][model_name]
        config_url = detectron2.catalog.CONFIG_CATALOG[dataset_name][model_name]

        if 'model' not in os.listdir():
            os.mkdir('model')

        config_file_path, model_file_path = None, None

        for url in [model_url, config_url]:
            filename = url.split('/')[-1].split('?')[0]
            save_to_path = f"model/" + filename
            if 'config' in filename:
                config_file_path = copy.deepcopy(save_to_path)
            if 'model_final' in filename:
                model_file_path = copy.deepcopy(save_to_path)
            if filename in os.listdir("model"):
                continue
            r = requests.get(url, stream=True, headers={'user-agent': 'Wget/1.16 (linux-gnu)'})

            with open(save_to_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)

        super().__init__(
            config_path=config_file_path,
            model_path=model_file_path,
            *args,
            **kwargs
        )
