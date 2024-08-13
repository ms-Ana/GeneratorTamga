import os 
import sys
import bpy
from bpy.types import Modifier
import cv2
import bmesh
import random

nameTamge = 'TMG_'
nameOBJ = 'ART_'
nameTexture = 'TXT_'
nameBackground = 'BGR_'

path = 'E:/TamgiBlender/'

# Использование пользовательских текстур
useMyTexture = True


# Ограницения генерации
###########################################

# Маштабирование тамги
scaleTamg = [0.2, 0.4]
# Растушевка границ рисунка тамги                 
randBorder = [-0.2, 0.2]
# Растояние между векселями тамги          
randBorderReduction = [0.055, 0.089]
# Использование границ рисунка тамги   
limitDeformBorder = False                
if limitDeformBorder :
    # Деформация внутри границ
    randDeform = [-1.7, 1.7]            
else :
    # Деформация вне границ и самих границ
    randDeform = [-0.6, 0.6]     
# Маштабирование объекта
scaleArt = [0.9, 1.5]       
# Наклон объекта архитектуры (Градусы)
angleArtX = [-17, 19] 
angleArtY = [-21, 24] 
angleArtZ = [-19, 10]
# Наклон тамги (Градусы)
angleTmgX = [-90.5, -89.5] 
angleTmgY = [0, 360]
# Использование обтягивания объекта тамгой
useWrap = False
# Вид проекции
viewType = 'TOP'    # LEFT / RIGHT / BOTTOM / TOP / FRONT / BACK
# Глубина вдавливания / выдавливания тамги
depthTmg = [-0.011, 0.016]
# Интенсивность освещения
sunEnergy = [3.5, 5.2]
# Позиции врашения
sunEulerX = [-50, -10]
sunEulerY = [-50, -20]
sunEulerZ = [15, 50]
# Угол освещения
sunAngle = [30, 55]
# Наклон камеры
rotareCamX = [-91.5, -89]
rotareCamY = [0, 360]  # Вращение
# Отдоление от объекта
distanceCam = [0.1, 0.7] # в Метрах, от исходного положения
# Разрешение в процентах
resolutionOut = 100


# Количество тамг
countTamgs = [0, 224]
# Количество объектов
countArtifacts = [0, 22]
# Количество текстур
countTextures = [0, 26]
# Количество фонов
countBackgrounds = 20

# Счетчик
totalCount = 0

###########################################


# Вспомогательные функции
###########################################

# Очистить все узлы в material
def clear_material( material ):
    if material.node_tree:
        material.node_tree.links.clear()
        material.node_tree.nodes.clear()
    return

# Получить область вида
def getArea(type):
    for screen in bpy.context.workspace.screens:
        if len(screen.areas) <= 0:
            raise Exception(f"Make sure an Area of type {area_type} is open or visible in your screen!")
        for area in screen.areas:
            if area.type == type:
                return area
            
# Очистить рабочую сцену
def clearScene():
    #
    if bpy.ops.object:
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
    for collection in bpy.data.collections:
        collection_del = bpy.data.collections.get(collection.name)
        for obj in collection_del.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(collection_del)
    return

def clearData():
    #
    for block in bpy.data.curves:
        bpy.data.curves.remove(block)
    #
    for block in bpy.data.lights:
        bpy.data.lights.remove(block)
    #
    for block in bpy.data.cameras:
        bpy.data.cameras.remove(block)
    #    
    for block in bpy.data.grease_pencils:
        bpy.data.grease_pencils.remove(block)
    #
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)
    #
    for block in bpy.data.images:
        bpy.data.images.remove(block)
    #
    for block in bpy.data.materials:
        if not block.users:
           bpy.data.materials.remove(block)
    #
    for block in bpy.data.textures:
        bpy.data.textures.remove(block)
    #
    bpy.data.batch_remove(bpy.data.cache_files)    
    return
            
###########################################



# Генерация
###########################################

numIterGeneretion = 0

for numberTMG in [1]: #range(countTamgs[0], countTamgs[1]):
    totalCount = 1
    rangeART = list(range(countArtifacts[0], countArtifacts[1]))
    random.shuffle(rangeART)
    rangeTXT = list(range(countTextures[0], countTextures[1]))
    random.shuffle(rangeTXT)
    for numberART in rangeART:
        for numberTXT in rangeTXT:

            # Получаем пути
            pathIMG = "{0}img/{1}{2}.jpg".format(path, nameTamge, numberTMG)
            pathOBJ = "{0}obj/{1}{2}.obj".format(path, nameOBJ, numberART)
            pathTEX = "{0}texture/{1}{2}.jpg".format(path, nameTexture, numberTXT)
            numberBGR = random.randint(0, countBackgrounds - 1)
            pathBGR = "{0}ground/{1}{2}.jpg".format(path, nameBackground, numberBGR)
            
            # Очистить всю рабочую зону
            clearScene()
            clearData()

            # Создание меша тамги
            ###########################################

            # Меш тамги
            workTamga = None

            # Считываем изображение тамги
            img_grey = cv2.imread(pathIMG, cv2.IMREAD_GRAYSCALE) 
            # Определяем порог, 128 — это середина черного и белого в шкале серого
            thresh = 128 
            # Переводим изображение в черно-белый 
            img_binary = cv2.threshold(img_grey, thresh, 255, cv2.THRESH_BINARY)[1] 
            # Сохраняем изображение 
            cv2.imwrite(path + "tmp/BlackAndWhite_" + str(numberTMG) + ".png", img_binary)

            # Загружаем черно-белое изображение в блендер
            bpy.ops.object.load_reference_image(filepath=path + "tmp/BlackAndWhite_" + str(numberTMG) + ".png")
            # Находим изображение и переводим в gpencil
            for ob in bpy.data.objects:
                if ob.empty_display_type == "IMAGE":
                    ob.location = (0, 0, 0) 
                    ob.name = "IMGTang"
                    ob.select_set(True)
                    bpy.context.view_layer.objects.active = ob
                    bpy.ops.gpencil.trace_image(target='NEW')
                else:
                    ob.select_set(False)
            #Удаляем изображение
            for ob in bpy.data.objects:
                if ob.name == "IMGTang":
                    ob.select_set(True)
                    bpy.context.view_layer.objects.active = ob
                else:
                    ob.select_set(False)
            bpy.ops.object.delete(use_global=False)        
               
            # gpencil переводим в line
            for ob in bpy.context.scene.objects:
                if ob.type == 'GPENCIL': 
                    ob.select_set(True)
                    ob.name = "GrencilTang"
                    bpy.context.view_layer.objects.active = ob
                else:
                    ob.select_set(False)
            win      = bpy.context.window
            scr      = win.screen
            areas3d  = [area for area in scr.areas if area.type == 'VIEW_3D']
            region   = [region for region in areas3d[0].regions if region.type == 'WINDOW']
            override = {'window': win,
                    'screen': scr,
                    'area'  : areas3d[0],
                    'region': region[0],
                    'scene' : bpy.context.scene} 
            for obj in bpy.context.selected_objects:
                bpy.ops.gpencil.convert(override, type='CURVE', timing_mode='LINEAR',  use_timing_data=False)
            # Удаляем gpencil
            for ob in bpy.context.scene.objects:
                if ob.name == "GrencilTang":
                    ob.select_set(True)
                    bpy.context.view_layer.objects.active = ob
                else:
                    ob.select_set(False)
            bpy.ops.object.delete(use_global=False) 

            # line в mesh
            for ob in bpy.context.scene.objects:
                if (ob.empty_display_type == "PLAIN_AXES"):
                    ob.name = "TraceTang"
                    mesh = bpy.data.meshes.new_from_object(ob)  
                    workTamga = bpy.data.objects.new('TAMGA', mesh)
                    workTamga.matrix_world = ob.matrix_world
                    bpy.context.collection.objects.link(workTamga)
            # Удаляем line
            for ob in bpy.context.scene.objects:
                if ob.name == "TraceTang":
                    ob.select_set(True)
                    bpy.context.view_layer.objects.active = ob
                else:
                    ob.select_set(False)
            bpy.ops.object.delete(use_global=False)   


            # Импорт объекта архитектуры
            ###########################################

            # Меш объекта
            workObject = None

            # Импортируем OBJ
            bpy.ops.wm.obj_import(
                filepath = pathOBJ, 
                directory = path + "obj/", 
                files=[{
                    "name" : "{0}{1}.obj".format(nameOBJ, numberART), 
                    "name" : "{0}{1}.obj".format(nameOBJ, numberART)}]
            )
            for ob in bpy.context.scene.objects:
                if ob.name != workTamga.name:
                    workObject = ob
                    workObject.name = "ARTIFACT"
                    continue
                
            # Режим предварительное редактирование
            workObject.select_set(True)
            bpy.context.view_layer.objects.active = workObject
            bpy.ops.object.mode_set(mode = 'EDIT')        
            bpy.ops.mesh.select_all(action = 'SELECT')    
            # Увеличиваем количество точек    
            bpy.ops.mesh.subdivide()   # Можно и два раза
            bpy.ops.mesh.subdivide()
            bpy.ops.object.mode_set(mode = 'OBJECT')  

            
            # Наложение выбраной текстуры
            ###########################################
            
            # Если нужна текстура 
            if useMyTexture :
                # получить материал
                mat = bpy.data.materials.get("Material")
                if mat is None:
                    # создать материал
                    mat = bpy.data.materials.new(name="Material")
                clear_material(mat)
                mat.use_nodes = True
                # Создания блоков настройки материала
                nodes = mat.node_tree.nodes
                links = mat.node_tree.links
                # Компоненты (блоки) материала
                output = nodes.new( type = 'ShaderNodeOutputMaterial' )
                output.location = (1500.0, 100.0)
                principled = nodes.new( type = 'ShaderNodeBsdfPrincipled' )
                principled.location = (700.0, 300.0)
                textureBase = nodes.new( type = 'ShaderNodeTexImage' )
                textureBase.location = (350.0, 100.0)
                # Связи 
                link = links.new( principled.outputs['BSDF'], output.inputs['Surface'] ) 
                link = links.new( textureBase.outputs['Color'], principled.inputs['Base Color'] )
                # Загрузка текстуры
                textureBase.image = bpy.data.images.load(pathTEX)
                # Задать объекту новую текстуру
                workObject.data.materials.clear()
                workObject.data.materials.append(mat)

            
            # Изменение размеров
            ########################################### 

            # Изменяем размеры объекта
            max = 0
            for i in range(3):
                if max < workObject.dimensions[i]:
                    max = workObject.dimensions[i]
            workObject.dimensions = (workObject.dimensions[0] / max, workObject.dimensions[1] / max, workObject.dimensions[2] / max) 
            workObject.scale[0] = workObject.scale[1] = workObject.scale[2] = workObject.scale[0] * (random.random() * (scaleArt[1] - scaleArt[0]) + scaleArt[0])
            # Перемещаем объект
            workObject.location = (0, 0, 0) 
                 
            # Изменяем размеры тамги
            max = 0
            for i in range(3):
                if max < workTamga.dimensions[i]:
                    max = workTamga.dimensions[i]
            workTamga.dimensions = (workTamga.dimensions[0] / max, workTamga.dimensions[1] / max, workTamga.dimensions[2] / max)
            workTamga.scale[0] = workTamga.scale[1] = workTamga.scale[2] = workTamga.scale[0] * (random.random() * (scaleTamg[1] - scaleTamg[0]) + scaleTamg[0]) 
            
            # Позиция тамги относительно объекта
            locationTmg = [
                random.random() * workObject.dimensions[0] * workObject.scale[0] / 8 - workObject.dimensions[0] * workObject.scale[0] / 16,
                -workObject.dimensions[2] * workObject.scale[2] / 1.25 - 0.25, 
                random.random() * workObject.dimensions[1] * workObject.scale[1] / 4 - workObject.dimensions[1] * workObject.scale[1] / 6
            ]
            workTamga.location = (locationTmg[0], locationTmg[1], locationTmg[2])
            

            # Деформация Тамги
            ###########################################

            # Создать пустой BMesh
            bmTamga = bmesh.new()
            # Помещаем данные Тамги в BMesh
            bmTamga.from_mesh(workTamga.data)
            # Упрошение - уменьшаем количество вертоксов стоящих слишком близко
            bmesh.ops.remove_doubles(bmTamga, verts = bmTamga.verts, dist = random.random() * (randBorderReduction[1] - randBorderReduction[0]) + randBorderReduction[0])
            # Работа с координатами (x,y,z) - растушевка положения точек на границах рисунка
            for v in bmTamga.verts:
                v.co.x = (v.co.x * 9 + v.co.x * (random.random() * (randBorder[1] - randBorder[0]) + randBorder[0])) / 10.0
                v.co.y = (v.co.y * 9 + v.co.y * (random.random() * (randBorder[1] - randBorder[0]) + randBorder[0])) / 10.0
                v.co.z = 0
            # Запишем BMesh обратно в меш Тамги
            bmTamga.verts.index_update()
            bmTamga.to_mesh(workTamga.data)
            # Освободить и предотвратить дальнейший доступ
            bmTamga.free()  

            # Создаем КУБ деформации
            bpy.ops.mesh.primitive_cube_add()
            cube = bpy.context.selected_objects[0]
            cube.name = "CubeDeform"
            # Положение центра как у тамги
            cube.location = workTamga.location
            cube.dimensions = workTamga.dimensions
            # Маштабируем куб чуть больше размеров тамги 
            maxScale = 0
            for i in range(3) :
                if workTamga.dimensions[i] / cube.dimensions[i] > maxScale :
                    maxScale = workTamga.dimensions[i] / cube.dimensions[i]
            # Тамга вписана в куб
            cube.scale = workTamga.scale * maxScale / (workTamga.scale[0] * 0.95)
            # Разбивка ребер куба
            cube.select_set(True)    
            bpy.context.view_layer.objects.active = cube   
            bpy.ops.object.mode_set(mode = 'EDIT')   
            # Увеличиваем количество точек    
            bpy.ops.mesh.subdivide()   # Можно и два раза
            bpy.ops.mesh.subdivide()
            # Выйти из режима редактирование 
            bpy.ops.object.mode_set(mode = 'OBJECT') 

            # Сортировка вертоксов
            bmCube = bmesh.new()
            bmCube.from_mesh(cube.data)
            bmCube.verts.sort(key=lambda v: 100 * v.co.z + 10 * v.co.y + v.co.x)
            rangeX = []     # Значения иксов
            rangeY = []     # Значения игриков
            for v in bmCube.verts:
                rangeX.append(v.co.x)
                rangeY.append(v.co.y)
            rangeX = list(set(rangeX))
            rangeX.sort()
            rangeY = list(set(rangeY))
            rangeY.sort()
            bmCube.verts.index_update()
            bmCube.to_mesh(cube.data)
            bmCube.free() 

            # Добавление модификатора деформации в меш Тамги
            deformMod = workTamga.modifiers.new("MeshDeform", 'MESH_DEFORM')
            deformMod.object = cube
            deformMod.precision = 0
            bpy.ops.object.meshdeform_bind(
                {
                    "object": workTamga, 
                    "active_object": workTamga, 
                    "scene": bpy.context.scene
                },
                modifier="MeshDeform"
            )

            # Создать пустой BMesh
            bmCube = bmesh.new()
            # Помещаем данные Cube в BMesh
            bmCube.from_mesh(cube.data)
            # Работа с координатами (x,y,z)
            for i in rangeX :
                for j in rangeY :
                    newX = i + (random.random() * (randDeform[1] - randDeform[0]) + randDeform[0])
                    newY = j + (random.random() * (randDeform[1] - randDeform[0]) + randDeform[0])
                    if limitDeformBorder :
                        if i != 1 and i != -1 and j != 1 and j != -1 :
                            for v in bmCube.verts :
                                if (v.co.x == i) and (v.co.y == j) :
                                    v.co.x = newX
                                    v.co.y = newY
                    else :
                        for v in bmCube.verts :
                            if (v.co.x == i) and (v.co.y == j) :
                                v.co.x = newX
                                v.co.y = newY    
            # Запишем BMesh обратно в меш Cube
            bmCube.verts.index_update()
            bmCube.to_mesh(cube.data)
            # Освободить и предотвратить дальнейший доступ
            bmCube.free() 

            # Применение модификатора деформации
            workTamga.select_set(True) 
            cube.select_set(False) 
            bpy.ops.object.modifier_apply(
                {
                    "object": workTamga, 
                    "active_object": workTamga, 
                    "scene": bpy.context.scene
                },
                modifier="MeshDeform"
            )

            # Удаляем КУБ деформации
            for ob in bpy.context.scene.objects:
                if ob.name == "CubeDeform":
                    ob.select_set(True)
                    bpy.context.view_layer.objects.active = ob
                else:
                    ob.select_set(False)
            bpy.ops.object.delete(use_global=False) 


            # Врашение мешев
            ###########################################

            # Врашение объекта
            workObject.select_set(True)
            workTamga.select_set(False)
            bpy.context.view_layer.objects.active = workObject
            rotateObj = [
                (random.random() * (angleArtX[1] - angleArtX[0]) + angleArtX[0]) * (3.14 / 180),
                (random.random() * (angleArtY[1] - angleArtY[0]) + angleArtY[0]) * (3.14 / 180),
                (random.random() * (angleArtZ[1] - angleArtZ[0]) + angleArtZ[0]) * (3.14 / 180)
            ]
            bpy.ops.transform.rotate(
                value = rotateObj[0],
                orient_axis='X',
                orient_type='GLOBAL', 
                orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), 
                orient_matrix_type='GLOBAL', 
                constraint_axis=(True, False, False), 
                mirror=False, 
                use_proportional_edit=False, 
                proportional_edit_falloff='SPHERE', 
                proportional_size=1, 
                use_proportional_connected=False, 
                use_proportional_projected=False, 
                snap=False, 
                snap_elements={'INCREMENT'}, 
                use_snap_project=False, 
                snap_target='CLOSEST', 
                use_snap_self=True, 
                use_snap_edit=True, 
                use_snap_nonedit=True, 
                use_snap_selectable=False, 
                release_confirm=True
            )
            bpy.ops.transform.rotate(
                value = rotateObj[1], 
                orient_axis='Y', 
                orient_type='GLOBAL', 
                orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), 
                orient_matrix_type='GLOBAL', 
                constraint_axis=(False, True, False), 
                mirror=False, 
                use_proportional_edit=False, 
                proportional_edit_falloff='SPHERE', 
                proportional_size=1, 
                use_proportional_connected=False, 
                use_proportional_projected=False, 
                snap=False, 
                snap_elements={'INCREMENT'}, 
                use_snap_project=False, 
                snap_target='CLOSEST', 
                use_snap_self=True, 
                use_snap_edit=True, 
                use_snap_nonedit=True, 
                use_snap_selectable=False, 
                release_confirm=True
            )
            bpy.ops.transform.rotate(
                value = rotateObj[2], 
                orient_axis='Z', 
                orient_type='GLOBAL', 
                orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), 
                orient_matrix_type='GLOBAL', 
                constraint_axis=(False, False, True), 
                mirror=False, 
                use_proportional_edit=False, 
                proportional_edit_falloff='SPHERE', 
                proportional_size=1, 
                use_proportional_connected=False, 
                use_proportional_projected=False, 
                snap=False, 
                snap_elements={'INCREMENT'}, 
                use_snap_project=False, 
                snap_target='CLOSEST', 
                use_snap_self=True, 
                use_snap_edit=True, 
                use_snap_nonedit=True, 
                use_snap_selectable=False, 
                release_confirm=True
            )

            # Врашение тамги
            workObject.select_set(False)
            workTamga.select_set(True)
            bpy.context.view_layer.objects.active = workTamga
            rotateTmg = [
                (random.random() * (angleTmgX[1] - angleTmgX[0]) + angleTmgX[0]) * (3.14 / 180),
                (random.random() * (angleTmgY[1] - angleTmgY[0]) + angleTmgY[0]) * (3.14 / 180)
            ]
            bpy.ops.transform.rotate(
                value = rotateTmg[0], 
                orient_axis='X', 
                orient_type='GLOBAL', 
                orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), 
                orient_matrix_type='GLOBAL', 
                constraint_axis=(True, False, False), 
                mirror=False, 
                use_proportional_edit=False, 
                proportional_edit_falloff='SPHERE', 
                proportional_size=1, 
                use_proportional_connected=False, 
                use_proportional_projected=False, 
                snap=False, 
                snap_elements={'INCREMENT'}, 
                use_snap_project=False, 
                snap_target='CLOSEST', 
                use_snap_self=True, 
                use_snap_edit=True, 
                use_snap_nonedit=True, 
                use_snap_selectable=False, 
                release_confirm=True
            )
            bpy.ops.transform.rotate(
                value = rotateTmg[1], 
                orient_axis='Y', 
                orient_type='GLOBAL', 
                orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), 
                orient_matrix_type='GLOBAL', 
                constraint_axis=(False, True, False), 
                mirror=False, 
                use_proportional_edit=False, 
                proportional_edit_falloff='SPHERE', 
                proportional_size=1, 
                use_proportional_connected=False, 
                use_proportional_projected=False, 
                snap=False, 
                snap_elements={'INCREMENT'}, 
                use_snap_project=False, 
                snap_target='CLOSEST', 
                use_snap_self=True, 
                use_snap_edit=True, 
                use_snap_nonedit=True, 
                use_snap_selectable=False, 
                release_confirm=True
                )
                                           
            # Обтягивание Тамги по форме объекта
            ###########################################
            
            # Если необходимо применить
            if useWrap :
                wrapMod = workTamga.modifiers.new("Shrinkwrap", 'SHRINKWRAP')
                wrapMod.wrap_method = 'TARGET_PROJECT'
                wrapMod.wrap_mode = 'ABOVE_SURFACE'
                wrapMod.target = workObject
                wrapMod.offset = 0.015
           
            # Выдавить / Вдавить Тамгу по форме на объекте
            ###########################################
 
            # Проецирование Тамги на объекте 
            for ns3d in getArea('VIEW_3D').spaces:
                if ns3d.type == "VIEW_3D":
                    break
            win      = bpy.context.window
            scr      = win.screen
            areas3d  = [getArea('VIEW_3D')]
            region   = [region for region in areas3d[0].regions if region.type == 'WINDOW']
            override = {'window':win,
                        'screen':scr,
                        'area'  :getArea('VIEW_3D'),
                        'region':region[0],
                        'scene' :bpy.context.scene,
                        'space' :getArea('VIEW_3D').spaces[0],
                        } 
            # Сброс всех активных состояний           
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = None
            # Выровнить вид по строго перпиндикулярно Тамге
            bpy.context.view_layer.objects.active = workTamga
            if ns3d.region_3d.view_perspective == 'PERSP':
                bpy.ops.view3d.view_persportho(override)
            bpy.ops.view3d.view_selected(override)
            # LEFT / RIGHT / BOTTOM / TOP / FRONT / BACK
            bpy.ops.view3d.view_axis(override, type=viewType, align_active=True)
            # Обновить область
            ns3d.region_3d.update()
            # Режим предварительное редактирование
            workObject.select_set(True)
            bpy.context.view_layer.objects.active = workObject
            bpy.ops.object.mode_set(mode = 'EDIT')
            # Выбрать все объекты над которыми будет производиться операция
            workObject.select_set(True)
            workTamga.select_set(True)
            # Проекция Тамги ножом на объекте
            bpy.ops.mesh.knife_project(override)  
            # Определение выдавливание или вдавливание проекции 
            valueDepth = random.random() * (depthTmg[1] - depthTmg[0]) + depthTmg[0]
            # Убираем около нулевое расстояние
            if (valueDepth > 0.0) and (valueDepth < 0.007) :
                valueDepth = 0.007
            if (valueDepth > -0.005) and (valueDepth <= 0.0) :
                valueDepth = -0.005
            # Выдавливание / Вдавливание проекции 
            bpy.ops.mesh.extrude_region_move(
                MESH_OT_extrude_region={
                    "use_normal_flip":False, 
                    "use_dissolve_ortho_edges":False, 
                    "mirror":False}, 
                TRANSFORM_OT_translate={
                    "value":(0, 0, valueDepth),  
                    "orient_axis_ortho":'X', 
                    "orient_type":'NORMAL', 
                    "orient_matrix":(
                        (-1, 0, 0),        
                        (0, 0, 1), 
                        (0, 1, 0)), 
                    "orient_matrix_type":'NORMAL', 
                    "constraint_axis":(False, False, True), 
                    "mirror":False, 
                    "use_proportional_edit":False, 
                    "proportional_edit_falloff":'SPHERE', 
                    "proportional_size":1, 
                    "use_proportional_connected":False, 
                    "use_proportional_projected":False, 
                    "snap":False, 
                    "snap_elements":{'INCREMENT'}, 
                    "use_snap_project":False, 
                    "snap_target":'CLOSEST', 
                    "use_snap_self":True,
                    "use_snap_edit":True, 
                    "use_snap_nonedit":True, 
                    "use_snap_selectable":False, 
                    "snap_point":(0, 0, 0), 
                    "snap_align":False, 
                    "snap_normal":(0, 0, 0), 
                    "gpencil_strokes":False, 
                    "cursor_transform":False, 
                    "texture_space":False, 
                    "remove_on_cancel":False, 
                    "view2d_edge_pan":False, 
                    "release_confirm":False, 
                    "use_accurate":False, 
                    "use_automerge_and_split":False})
            # Разделяем меш на область выдавленой/выразенной и самого артифакта
            bpy.ops.mesh.separate(type='SELECTED')
            # Выйти из режима редактирования в 
            bpy.ops.object.mode_set(mode = 'OBJECT')        
            
            # Часть меша помещаем в переменную
            workKnife = None
            for ob in bpy.context.scene.objects:
                if ob.name != workObject.name and ob.name != workTamga.name :
                    workKnife = ob
                    workKnife.name = "KNIFE"
            
            # Удалить тамгу
            workObject.select_set(False)
            workKnife.select_set(False)
            workTamga.select_set(True)
            bpy.ops.object.delete(use_global=False)
            workTamga = None


            # Работа со светом и камерой
            ###########################################

            # Создать основной световой блок
            lightData = bpy.data.lights.new(name="myLight", type='SUN')
            # Создаем объект и передаем данные о свете
            lightObject = bpy.data.objects.new(name="myLightSUN", object_data=lightData)
            # Помешение объекта освещения на сцену
            bpy.context.collection.objects.link(lightObject)
            # Изменение позиции
            lightObject.location = (
                random.random() * 200 - 100, 
                random.random() * 100 - 50, 
                random.random() * 20 - 10
            )  
            # Вращение вокруг выбранной позиции
            angle_euler = [
                (random.random() * (sunEulerX[1] - sunEulerX[0]) + sunEulerX[0]) * (3.14 / 180),
                (random.random() * (sunEulerY[1] - sunEulerY[0]) + sunEulerY[0]) * (3.14 / 180),
                (random.random() * (sunEulerZ[1] - sunEulerZ[0]) + sunEulerZ[0]) * (3.14 / 180),
            ]
            lightObject.rotation_euler = (
                angle_euler[0],
                angle_euler[1],
                angle_euler[2]
            )
            # интенсивность всета
            lightData.energy = random.random() * (sunEnergy[1] - sunEnergy[0]) + sunEnergy[0]
            # Угол освещения
            lightObject.data.angle = (random.random() * (sunAngle[1] - sunAngle[0]) + sunAngle[0]) * (3.14 / 180)
            # Цвет света
            lightObject.data.color = (1, 0.9, 0.75)
            
            # Создать дополнительный свет
            # Создаем объект и передаем данные о свете
            lightObjectAdd = bpy.data.objects.new(name="myLightAddSUN", object_data=lightData)
            # Помешение объекта освещения на сцену
            bpy.context.collection.objects.link(lightObjectAdd)
            # Изменение позиции
            lightObjectAdd.location = (
                random.random() * -10 - 5,
                random.random() * -50 + 25,
                random.random() * -100 - 50
            )  
            # Вращение вокруг выбранной позиции
            angle_euler = [
                (random.random() * (sunEulerX[1] - sunEulerX[0]) + sunEulerX[0]) * (3.14 / 180),
                (random.random() * (sunEulerY[1] - sunEulerY[0]) + sunEulerY[0]) * (3.14 / 180),
                (random.random() * (sunEulerZ[1] - sunEulerZ[0]) + sunEulerZ[0]) * (3.14 / 180),
            ]
            lightObjectAdd.rotation_euler = (
                angle_euler[2],
                angle_euler[1],
                angle_euler[0]
            )
            # интенсивность всета
            lightData.energy = random.random() / 2 * (sunEnergy[1] - sunEnergy[0]) + sunEnergy[0]
            # Угол освещения
            lightObjectAdd.data.angle = (random.random() * (sunAngle[1] - sunAngle[0]) + sunAngle[0]) * (3.14 / 180)
            # Цвет света
            lightObjectAdd.data.color = (0.9, 0.95, 1) 

            # Камера
            cameraData = bpy.data.cameras.new(name='myCamera')
            cameraObject = bpy.data.objects.new('myCamera', cameraData)
            bpy.context.scene.collection.objects.link(cameraObject)
            cameraObject.location = (
                locationTmg[0], 
                workObject.dimensions[2] * 1.0 + (random.random() * (distanceCam[1] - distanceCam[0]) + distanceCam[0]), 
                locationTmg[2]
            )
            # Выбор камеры 
            for ob in bpy.context.scene.objects:
                if ob.name == "myCamera":
                    ob.select_set(True)
                    bpy.context.view_layer.objects.active = ob
                else:
                    ob.select_set(False)
            # Врашение камер
            rotateCamera = [
                (random.random() * (rotareCamX[1] - rotareCamX[0]) + rotareCamX[0]) * (3.14 / 180),
                (random.random() * (rotareCamY[1] - rotareCamY[0]) + rotareCamY[0]) * (3.14 / 180)
            ]
            bpy.ops.transform.rotate(
                value = rotateCamera[0], 
                orient_axis='X', 
                orient_type='GLOBAL', 
                orient_matrix=(
                    (1, 0, 0), 
                    (0, 1, 0), 
                    (0, 0, 1)), 
                orient_matrix_type='GLOBAL', 
                constraint_axis=(True, False, False), 
                mirror=False, 
                use_proportional_edit=False, 
                proportional_edit_falloff='SPHERE',
                proportional_size=1, 
                use_proportional_connected=False, 
                use_proportional_projected=False, 
                snap=False, 
                snap_elements={'INCREMENT'}, 
                use_snap_project=False, 
                snap_target='CLOSEST', 
                use_snap_self=True, 
                use_snap_edit=True, 
                use_snap_nonedit=True, 
                use_snap_selectable=False, 
                release_confirm=True
            )
            bpy.ops.transform.rotate(
                value = rotateCamera[1], 
                orient_axis='Y', 
                orient_type='GLOBAL', 
                orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), 
                orient_matrix_type='GLOBAL', 
                constraint_axis=(False, True, False), 
                mirror=False, 
                use_proportional_edit=False, 
                proportional_edit_falloff='SPHERE', 
                proportional_size=1, 
                use_proportional_connected=False, 
                use_proportional_projected=False, 
                snap=False, 
                snap_elements={'INCREMENT'}, 
                use_snap_project=False, 
                snap_target='CLOSEST', 
                use_snap_self=True, 
                use_snap_edit=True, 
                use_snap_nonedit=True, 
                use_snap_selectable=False, 
                release_confirm=True
            )    
        
            # Загрузка заднего фона 
            ###########################################
            
            # Загружаем изображение 
            imgBack = bpy.data.images.load(pathBGR)
            # Устанавливаем задний фон на камеру
            cameraObject.data.show_background_images = True
            bg = cameraObject.data.background_images.new()
            # Помещаем изображение на задний фон 
            bg.image = imgBack
            # Прозрачная сцена
            bpy.context.scene.render.film_transparent = True
            

            # Сохранение рендеров
            ###########################################
            
            # Рендер 3D сцены
            # Активная сцена
            bpy.context.scene.use_nodes = True
            # Ограничение семплов
            bpy.context.scene.cycles.samples = 1 
             # Активная камера
            bpy.context.scene.camera = cameraObject
            # Компоненты рендеринга в изображение
            tree = bpy.context.scene.node_tree
            # Чистим компоненты
            for every_node in tree.nodes:
                tree.nodes.remove(every_node)
            # Добавляем новые компоненты
            RenderLayers_node = tree.nodes.new('CompositorNodeRLayers') 
            RenderLayers_node.location = (-400, 0)
            Comp_node = tree.nodes.new('CompositorNodeComposite')   
            Comp_node.location = (200, 200)
            Output_node = tree.nodes.new(type='CompositorNodeOutputFile')
            Output_node.location = (200, -200) 
            Output_node.base_path = path + "tmp/"    # Куда сохранять
            Output_node.format.file_format  = "PNG"     # Формат            
            AplhaOver_node = tree.nodes.new(type="CompositorNodeAlphaOver")
            AplhaOver_node.location = (-50, 200)
            Scale_node = tree.nodes.new(type="CompositorNodeScale")
            Scale_node.space = 'RENDER_SIZE'
            Scale_node.location = (-400, 200)
            Image_node = tree.nodes.new(type="CompositorNodeImage")
            Image_node.image = imgBack  
            Image_node.location = (-650, 200)           
            # Связи компонентов
            links = tree.links
            link1 = links.new(RenderLayers_node.outputs[0], AplhaOver_node.inputs[2])
            link2 = links.new(RenderLayers_node.outputs[0], Output_node.inputs[0])
            link3 = links.new(AplhaOver_node.outputs[0], Comp_node.inputs[0])
            link4 = links.new(Scale_node.outputs[0], AplhaOver_node.inputs[1])
            link5 = links.new(Image_node.outputs[0], Scale_node.inputs[0])
            #
            totalCount += 1
            internalDir = "val" if (totalCount % 5 == 0) else "train"
            # Задаем путь сохранения готового изображения
            bpy.context.scene.render.resolution_x = 600
            bpy.context.scene.render.resolution_y = 600
            bpy.context.scene.render.resolution_percentage = resolutionOut
            bpy.context.scene.render.image_settings.compression = 50
            bpy.context.scene.render.image_settings.color_mode = 'RGB'
            bpy.context.scene.render.image_settings.file_format = 'PNG'
            bpy.context.scene.render.filepath = "{0}data/images/{1}/{2}a{3}a{4}_{5}.png".format(path, internalDir, numberTMG, numberART, numberTXT, numIterGeneretion)
            # Рендер активной сцены, вид с камеры
            bpy.ops.render.render(write_still=True, use_viewport=True)

            # Рендер Маски тамги на 3D сцене
            # Удаляем связь на вывод
            tree.links.remove(link2)
            # Добавляем новые компоненты
            Chroma_node = tree.nodes.new('CompositorNodeChromaMatte')
            Chroma_node.location = (-50, -100)
            Chroma_node.tolerance = 0.1
            Chroma_node.threshold = 0.0
            Comp_node2 = tree.nodes.new('CompositorNodeComposite')   
            Comp_node2.location = (200, 0)
            # Связи компонентов 
            link6 = links.new(RenderLayers_node.outputs[0], Chroma_node.inputs[0])
            link7 = links.new(Chroma_node.outputs[1], Output_node.inputs[0])
            link8 = links.new(Chroma_node.outputs[1], Comp_node2.inputs[0])
            # Удаляем основной объект
            for ob in bpy.context.scene.objects:
                ob.select_set(False)
            workObject.select_set(True)
            bpy.context.view_layer.objects.active = ob
            bpy.ops.object.delete(use_global=False)
            # Задаем путь сохранения маски изображения
            bpy.context.scene.render.resolution_x = 600
            bpy.context.scene.render.resolution_y = 600
            bpy.context.scene.render.resolution_percentage = resolutionOut
            bpy.context.scene.render.image_settings.compression = 95
            bpy.context.scene.render.image_settings.color_mode = 'BW'
            bpy.context.scene.render.image_settings.file_format = 'PNG'
            bpy.context.scene.render.filepath = "{0}data/masks/{1}/{2}a{3}a{4}_{5}.png".format(path, internalDir, numberTMG, numberART, numberTXT, numIterGeneretion)
            # Рендер активной сцены, вид с камеры
            bpy.ops.render.render(write_still=True, use_viewport=True)


