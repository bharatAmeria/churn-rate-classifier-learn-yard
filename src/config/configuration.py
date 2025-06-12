from src.entity.config_entity import *
from src.utils.common import read_yaml, create_directories
from src.constants import CONFIG_FILE_PATH, PARAMS_FILE_PATH


class ConfigurationManager:
    def __init__(self, config_filepath=CONFIG_FILE_PATH, params_filepath=PARAMS_FILE_PATH):
        self.config = read_yaml(config_filepath)
        self.params = read_yaml(params_filepath)

        create_directories([self.config.artifacts_root])

    def get_data_ingestion_config(self) -> DataIngestionConfig:
        config = self.config.data_ingestion

        create_directories([config.root_dir])

        data_ingestion_config = DataIngestionConfig(
            root_dir = config.root_dir,
            source_URL = config.source_URL,
            local_data_file = config.local_data_file,
            unzip_dir = config.unzip_dir,
        )

        return data_ingestion_config
    
    def get_data_cleaning_config(self) -> DataCleaningConfig:
        config = self.config.data_cleaning

        create_directories([config.cleaned_data_dir])

        data_cleaning_config = DataCleaningConfig(
            cleaned_data_dir = config.cleaned_data_dir, 
            cleaned_gurgaon_data = config.cleaned_gurgaon_data_path,
            missing_value_imputed = config.missing_value_imputed,
            gurgaon_data_path= config.gurgaon_houses_data_path,
            gurgaon_flats_data= config.gurgaon_flats_data_path,
            gurgaon_appartments_data = config.gurgaon_appartments_data_path,
            gurgaon_houses_data= config.gurgaon_houses_data_path
        )

        return data_cleaning_config
    
    def get_data_visualization_config(self) -> DataVisualizationConfig:
        config = self.config.data_visualization

        create_directories([config.viz_dir])

        data_viz_config = DataVisualizationConfig(
            viz_dir = config.viz_dir,
            feature_text = config.feature_text,
            missing_value_imputed = config.missing_value_imputed,
            latlong = config.latlong_data,
            data_viz = config.data_viz,
            gurgaon_properties = config.gurgaon_properties,
        )

        return data_viz_config
    
    def get_recommend_sys_config(self) -> RecommendSysConfig:
        config = self.config.recommend_sys

        create_directories([config.recommend_dir])

        recommend_sys_config = RecommendSysConfig(
            recommend_dir = config.recommend_dir,    
            appartments_path = config.appartments_path,
            cosine1 = config.cosine1,
            cosine2 = config.cosine2,
            cosine3 = config.cosine3,
        )

        return recommend_sys_config
