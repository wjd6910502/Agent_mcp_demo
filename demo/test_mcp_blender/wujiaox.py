import bpy
import math
import random
from mathutils import Vector
from colorsys import hsv_to_rgb

# 全局参数配置
STAR_RADIUS = 5.0
TOTAL_POINTS = 100
current_step = 0  # 当前生成进度
blink_timer = 0  # 闪烁计时器
spheres = []  # 存储所有球体的引用

# 清除场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

def create_red_material(step_num):
    """创建红色材质"""
    mat = bpy.data.materials.new(name=f"RedMat_{step_num:03d}")
    mat.use_nodes = True
    
    # 获取节点树
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # 清除默认节点
    nodes.clear()
    
    # 创建输出节点
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)
    
    # 创建混合着色器
    mix = nodes.new('ShaderNodeMixShader')
    mix.location = (100, 0)
    
    # 创建发光着色器
    emission = nodes.new('ShaderNodeEmission')
    emission.location = (-100, 100)
    emission.inputs['Color'].default_value = (1, 0, 0, 1)  # 红色
    emission.inputs['Strength'].default_value = 2.0
    
    # 创建BSDF着色器
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (-100, -100)
    bsdf.inputs['Base Color'].default_value = (1, 0, 0, 1)  # 红色
    bsdf.inputs['Metallic'].default_value = 0.8
    bsdf.inputs['Roughness'].default_value = 0.2
    
    # 连接节点
    links.new(emission.outputs[0], mix.inputs[1])
    links.new(bsdf.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], output.inputs[0])
    
    # 设置混合因子
    mix.inputs[0].default_value = 0.3  # 30%发光，70%BSDF
    
    return mat

def blink_random_spheres():
    """随机闪烁球体"""
    global spheres
    
    if len(spheres) > 0:
        # 随机选择1-3个球体进行闪烁
        num_to_blink = random.randint(1, min(3, len(spheres)))
        spheres_to_blink = random.sample(spheres, num_to_blink)
        
        for sphere in spheres_to_blink:
            if sphere and sphere.data.materials:
                # 获取材质
                mat = sphere.data.materials[0]
                if mat.use_nodes:
                    # 找到发光节点并调整强度
                    for node in mat.node_tree.nodes:
                        if node.type == 'EMISSION':
                            # 随机闪烁强度
                            node.inputs['Strength'].default_value = random.uniform(0.5, 5.0)
                            break
    
    return 1.0  # 每秒执行一次

def create_component():
    global current_step, spheres
    
    if current_step >= TOTAL_POINTS:
        return None  # 停止定时器
    
    # 计算五角星坐标
    theta = math.pi * 2 * current_step / TOTAL_POINTS
    r = STAR_RADIUS * (1 + 0.4 * math.cos(5 * theta))
    x = r * math.cos(theta)
    y = r * math.sin(theta)
    z = 3 * math.sin(5 * theta)
    
    # 创建球体
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.15,
        location=(x, y, z),
        scale=(1, 1, 1 + 0.3*math.cos(theta))
    )
    sphere = bpy.context.object
    sphere.name = f"StarPoint_{current_step:03d}"
    
    # 设置红色材质
    mat = create_red_material(current_step)
    sphere.data.materials.append(mat)
    
    # 将球体添加到列表中
    spheres.append(sphere)
    
    current_step += 1
    return 0.1  # 返回下次调用的时间间隔（秒）

# 设置场景环境
bpy.ops.object.light_add(type='SUN', location=(10, -10, 15))
sun = bpy.context.object
sun.data.energy = 5.0

# 设置相机
bpy.ops.object.camera_add(location=(15, -15, 10))
camera = bpy.context.object
camera.rotation_euler = (0.8, 0, 0.8)
bpy.context.scene.camera = camera

# 设置渲染属性
bpy.context.scene.render.film_transparent = True
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

# 设置世界环境
world = bpy.context.scene.world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.01, 0.01, 0.01, 1)

# 启动定时器
bpy.app.timers.register(create_component)
#bpy.app.timers.register(blink_random_spheres)

# 实时渲染刷新设置
bpy.context.preferences.view.show_developer_ui = True
bpy.context.scene.render.use_sequencer = False

print("红色五角星动画开始生成！每个球体间隔0.1秒，每秒随机闪烁...")
