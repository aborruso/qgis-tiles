import glob
import os
from osgeo import gdal
import sys
import shutil


# python3 utils/create-cog.py "qgis/full-nz-mono.qgz" 32000000,16000000,8000000 


def main(sorted_scales, root_scale, ovr_name):
    for scale in sorted_scales:
        vrt_list = []
        if scale != root_scale:
            for f in glob.glob(f'{QGIS_TILES}/**/{str(scale)}_gtiff_images.tif', recursive=True):
                vrt_list.append(f)
            
            # Build VRT
            gdal.BuildVRT(
                f"{VRT_DIR}/{str(scale)}k.vrt",
                vrt_list
            )
            
            creation_options = [
                "PROFILE=BASELINE",
                "BIGTIFF=YES"
            ]
        
            # Export VRT as Image
            print(f"Process overview: {scale}")
            ovr_name = f"{ovr_name}{OVR_EXT}"
            gdal.Translate(
                ovr_name,        
                f"{VRT_DIR}/{str(scale)}k.vrt",
                format = "GTiff",
                resampleAlg = "bilinear",
                creationOptions = creation_options,
                callback = gdal.TermProgress_nocb 
            )
            
        # Process Root Scale    
        elif scale == root_scale:
            for f in glob.glob(f'{QGIS_TILES}/**/{str(scale)}_gtiff_images.tif', recursive=True):
                vrt_list.append(f)
            
            # Build VRT
            gdal.BuildVRT(
                f"{VRT_DIR}/{str(scale)}k.vrt",
                vrt_list
            )
            
            creation_options = [
                "TILED=YES",
                "COMPRESS=JPEG",
                "BIGTIFF=YES"
            ]

            # Export VRT as Image
            gdal.Translate(
                f"{COG_OUTPUTS}/{str(scale)}k.tif",        
                f"{VRT_DIR}/{str(scale)}k.vrt",
                format = "GTiff",
                resampleAlg = "bilinear",
                creationOptions = creation_options,
                callback = gdal.TermProgress_nocb 
            ) 
            
        else:
            print("Scale is not an int")
        
    # create cog 
    creation_options = [
        "COMPRESS=JPEG",
        "BIGTIFF=YES",
        "NUM_THREADS=ALL_CPUS"
    ]

    # Save stack as COG
    print("Creating COG")
    gdal.SetConfigOption('RESAMPLING', 'BILINEAR')
    gdal.Translate(
        f"{COG_OUTPUTS}/{str(root_scale)}k_cog.tif",        
        f"{COG_OUTPUTS}/{str(root_scale)}k.tif",
        format = "COG",
        creationOptions = creation_options,
        callback = gdal.TermProgress_nocb 
    )

if __name__ == "__main__":    
    PROJECT_PATH = sys.argv[1]
    SCALES = sys.argv[2].split(",")
    GRID = "qgis/qgis-data/grids/100k_grid.gpkg"
    OUT_DIR = "tiles"

    DIR_NAME = os.path.basename(PROJECT_PATH).split(".")[0]
    QGIS_TILES = os.path.join(OUT_DIR, "qgis-grids", DIR_NAME)
    COG_OUTPUTS = os.path.join(OUT_DIR, "cog-outputs", DIR_NAME)
    VRT_DIR = os.path.join(OUT_DIR, "qgis-grids")

    if os.path.isdir(COG_OUTPUTS):
        shutil.rmtree(COG_OUTPUTS)
        os.makedirs(COG_OUTPUTS, exist_ok=True)
     
    # Remove all old vrt   
    test = os.listdir(VRT_DIR)

    for item in test:
        if item.endswith(".vrt"):
            os.remove(os.path.join(VRT_DIR, item))
        
    # set scale
    int_scales = [int(x) for x in SCALES]
    sorted_scales = sorted(int_scales, reverse=False)
    root_scale = min(int_scales)

    # Process scales to tifs
    OVR_EXT = ".ovr"
    ovr_name = f"{COG_OUTPUTS}/{int(root_scale)}k.tif"
    main(sorted_scales, root_scale, ovr_name)
