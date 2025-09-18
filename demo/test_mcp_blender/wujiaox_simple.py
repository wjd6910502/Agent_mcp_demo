import bpy
import math
from colorsys import hsv_to_rgb

# 简化参数配置
STAR_RADIUS = 3.0
TOTAL_POINTS = 20  # 减少球体数量，加快测试
current_step = 0

# 清除场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

def create_simple_material(hue):
    """创建简单的彩虹色材质"""
    r, g, b = hsv_to_rgb(hue, 0.8, 0.9)
    mat = bpy.data.materials.new(name=f"Color_{current_step:02d}")
    mat.use_nodes = True
    
    # 获取BSDF节点
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (r, g, b, 1)
    bsdf.inputs["Metallic"].default_value = 0.5
    bsdf.inputs["Roughness"].default_value = 0.3
    
    return mat

def create_component():
    global current_step
    
    if current_step >= TOTAL_POINTS:
        print(f"完成！生成了 {TOTAL_POINTS} 个球体")
        return None  # 停止定时器
    
    # 计算五角星坐标
    theta = math.pi * 2 * current_step / TOTAL_POINTS
    r = STAR_RADIUS * (1 + 0.3 * math.cos(5 * theta))
    x = r * math.cos(theta)
    y = r * math.sin(theta)
    z = 2 * math.sin(5 * theta)
    
    # 创建球体
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.2,
        location=(x, y, z),
        scale=(1, 1, 1 + 0.2*math.cos(theta))
    )
    sphere = bpy.context.object
    sphere.name = f"Star_{current_step:02d}"
    
    # 设置材质
    hue = current_step / TOTAL_POINTS
    mat = create_simple_material(hue)
    sphere.data.materials.append(mat)
    
    current_step += 1
    print(f"生成球体 {current_step}/{TOTAL_POINTS}")
    return 0.2  # 增加间隔到0.2秒，便于观察

# 设置场景环境
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
sun = bpy.context.object
sun.data.energy = 3.0

# 设置相机
bpy.ops.object.camera_add(location=(8, -8, 6))
camera = bpy.context.object
camera.rotation_euler = (0.7, 0, 0.7)
bpy.context.scene.camera = camera

# 设置渲染属性
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 64

# 设置世界环境
world = bpy.context.scene.world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.05, 0.05, 1)

# 启动定时器
bpy.app.timers.register(create_component)

print(f"开始生成五角星动画！")
print(f"参数: 半径={STAR_RADIUS}, 球体数量={TOTAL_POINTS}")
print(f"每个球体间隔0.2秒...")
