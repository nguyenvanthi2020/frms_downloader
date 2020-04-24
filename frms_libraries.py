from itertools import groupby
import pathlib
from pathlib import Path
import simplejson as json
import json
from json import *

def docdstinh():
    dir1 = str(Path(__file__).parent.absolute()) + '\jsons\provincelist.json'
    with open(dir1) as f1:
        datax1 = json.load(f1)
        return datax1
def docdshuyen():
    dir2 = str(Path(__file__).parent.absolute()) + '\jsons\districtlist.json'
    with open(dir2) as f2:
        datax2 = json.load(f2)
        return datax2
        
def docdsxa():
    dir3 = str(Path(__file__).parent.absolute()) + '\jsons\communelist.json'
    with open(dir3) as f3:
        datax3 = json.load(f3)
        return datax3

def query(syntax):
    sql = """(SELECT 
    ROW_NUMBER() OVER() as tt, 
    0 as id, 
    province.province_code matinh, 
    district.district_code mahuyen, 
    plot.commune_code maxa, 
    commune.name as xa, 
    plot.compt_code tk, 
    plot.sub_compt_code khoanh, 
    plot.plot_code lo, 
    plot.parcel_code thuad, 
    plot.map_sheet tobando, 
    plot.village ddanh, 
    plot.area dtich, 
    plot.forest_org_code nggocr, 
    ft.abbreviation as ldlr, 
    plot.forest_type_code maldlr, 
    _formis_get_tree_spec_abbr(plot.tree_spec_code) sldlr, 
    plot.planting_year namtr, 
    plot.avg_year_canopy captuoi, 
    0 as ktan, 
    plot.plant_state_code thanhrung, 
    plot.volume_per_ha mgo, 
    plot.volume_per_plot mgolo, 
    plot.stem_per_ha mtn, 
    plot.stem_per_plot mtnlo, 
    plot.p_forest_org_code nggocrt, 
    plot.site_cond_code as lapdia, 
    up.forest_func_main_code malr3, 
    up.abbreviation mdsd, 
    plot.forest_func_sub_code mamdsd, 
    fuo.actor_type_code dtuong, 
    fuo.actor_name churung, 
    plot.actor_id machur, 
    plot.conflict_sit_code trchap, 
    plot.land_use_cert_code quyensd, 
    plot.land_use_terune thoihansd, 
    plot.prot_contr_code khoan, 
    plot.forest_use_sit_code nqh, 
    fuonk.actor_name AS nguoink, 
    fuotrch.actor_name AS nguoitrch, 
    plot.actor_id_conflict mangnk, 
    plot.actor_id_prot mangtrch, 
    plot.nar_for_org_code ngsinh, 
    0 as kd, 
    0 as vd, 
    0 as capkd, 
    0 as capvd, 
    plot.old_plot_code locu, 
    plot.pos_status_code vitrithua, 
    province.name AS tinh, 
    district.name AS huyen, 
    plot.geom 
   FROM plot plot 
     LEFT JOIN plot_position_status pps ON plot.pos_status_code::numeric = pps.pos_status_code  
     LEFT JOIN commune commune ON plot.commune_code = commune.commune_code 
     LEFT JOIN district district ON commune.district_code = district.district_code 
     LEFT JOIN province province ON district.province_code = province.province_code 
     LEFT JOIN protection_contract pc ON plot.prot_contr_code = pc.prot_contr_code and pc.lang= 'vi' 
     LEFT JOIN forest_origin foc ON plot.forest_org_code = foc.forest_org_code and foc.lang= 'vi' 
     LEFT JOIN forest_type ft ON plot.forest_type_code = ft.forest_type_code and ft.lang= 'vi' 
     LEFT JOIN forest_use_situation fus ON plot.forest_use_sit_code = fus.forest_use_sit_code and fus.lang= 'vi' 
     LEFT JOIN p_forest_origin pfo ON plot.p_forest_org_code = pfo.p_forest_org_code and pfo.lang= 'vi' 
     LEFT JOIN conflict_situation ls ON plot.conflict_sit_code = ls.conflict_sit_code and ls.lang= 'vi' 
     LEFT JOIN natural_forest_origin ps ON plot.nar_for_org_code = ps.nar_for_org_code and ps.lang= 'vi' 
     LEFT JOIN site_condition scc ON plot.site_cond_code = scc.site_cond_code and scc.lang= 'vi' 
     LEFT JOIN forest_function up ON plot.forest_func_sub_code = up.forest_func_sub_code and up.lang= 'vi' 
     LEFT JOIN land_use_certificate urs ON plot.land_use_cert_code = urs.land_use_cert_code and urs.lang= 'vi' 
     LEFT JOIN forest_actor fuo ON fuo.commune_code = plot.commune_code AND fuo.actor_id = plot.actor_id 
     LEFT JOIN forest_actor fuotrch ON fuotrch.commune_code = plot.commune_code AND fuotrch.actor_id = plot.actor_id_conflict 
     LEFT JOIN forest_actor fuonk ON fuonk.commune_code = plot.commune_code AND fuonk.actor_id = plot.actor_id_prot 
   where plot.commune_code in (select commune_code from commune where district_code in ( 
   select district_code from district where """ + syntax + """)))"""
    return sql