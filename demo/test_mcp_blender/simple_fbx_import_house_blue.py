#!/usr/bin/env python3
"""
简单FBX文件导入工具
功能：清空场景 + 导入FBX模型 + 自动调整视图
"""

import bpy
import os

# ============================================================================
# 清除场景 - 在导入模块后立即执行
# ============================================================================
print("🧹 清空场景...")
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 清空所有材质
for mat in bpy.data.materials:
    bpy.data.materials.remove(mat, do_unlink=True)

# 清空所有网格数据
for mesh in bpy.data.meshes:
    bpy.data.meshes.remove(mesh, do_unlink=True)

print("✅ 场景已清空")

# ============================================================================
# 主要功能函数
# ============================================================================

def safe_view_all():
    """安全地调整视图，避免区域错误"""
    try:
        # 检查是否有3D视图区域
        view3d_areas = [area for area in bpy.context.screen.areas if area.type == 'VIEW_3D']
        if view3d_areas:
            # 设置活动区域为3D视图
            bpy.context.window.workspace = bpy.context.workspace
            bpy.context.window.screen = bpy.context.screen
            bpy.context.window.area = view3d_areas[0]
            bpy.context.window.region = view3d_areas[0].regions[0]
            
            bpy.ops.view3d.view_all(center=True)
            return True
        else:
            print("⚠️ 未找到3D视图区域")
            return False
    except Exception as e:
        print(f"⚠️ 视图调整失败: {e}")
        return False

def find_best_material():
    """智能查找最佳材质"""
    available_materials = list(bpy.data.materials)
    if not available_materials:
        return None
    
    # 优先查找包含特定关键词的材质
    preferred_keywords = ['yellow']
    
    for material in available_materials:
        # 获取材质的名称字符串，然后转换为小写进行比较
        mat_name = material.name
        mat_lower = mat_name.lower()
        if any(keyword in mat_lower for keyword in preferred_keywords):
            print(f"🎯 找到匹配的材质: {mat_name}")
            return material
    
    # 如果没有找到匹配的，返回第一个
    print(f"🔄 使用默认材质: {available_materials[0].name}")
    return available_materials[0]

def simple_import_fbx(fbx_file_path):
    """简单的FBX导入流程"""
    
    print("🚀 开始FBX导入流程...")
    
    # 检查文件是否存在
    if not os.path.exists(fbx_file_path):
        print(f"❌ 文件不存在: {fbx_file_path}")
        print("💡 请检查文件路径是否正确")
        return False
    
    # 导入FBX文件
    try:
        print(f"📥 正在导入: {os.path.basename(fbx_file_path)}")
        bpy.ops.import_scene.fbx(filepath=fbx_file_path)
        print("✅ 导入成功！")
        
        # 调整视图
        print("👁️ 调整视图...")
        if safe_view_all():
            print("✅ 视图调整成功！")
        else:
            print("💡 视图调整失败，但这不会影响模型导入")
            print("💡 你可以在Blender中手动按数字键盘的 '.' 键来调整视图")
        
        # 显示导入的对象信息
        imported_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
        if imported_objects:
            print(f"📊 成功导入 {len(imported_objects)} 个网格对象")
            for obj in imported_objects:
                print(f"   - {obj.name} (顶点数: {len(obj.data.vertices)})")
        
        print("🎉 导入完成！")
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def import_material(blend_file):
    """导入材质"""
    
    # 检查文件是否存在
    if not os.path.exists(blend_file):
        print(f"文件不存在: {blend_file}")
        return False
    
    try:
        # 先查看可用的材质
        with bpy.data.libraries.load(blend_file, link=False) as (data_from, data_to):
            available_materials = list(data_from.materials)
            print(f"📋 可用的材质: {available_materials}")
            
            if not available_materials:
                print("❌ 文件中没有找到任何材质")
                return False
            
            # 智能选择最佳材质
            best_material = None
            preferred_keywords = ['blue', 'tile', 'colour', 'color']
            
            for mat_name in available_materials:
                mat_lower = mat_name.lower()
                if any(keyword in mat_lower for keyword in preferred_keywords):
                    best_material = mat_name
                    break
            
            if not best_material:
                best_material = available_materials[0]  # 使用第一个作为默认
            
            print(f"🎯 选择材质: {best_material}")
            
            # 导入选中的材质
            data_to.materials.append(best_material)
            print(f"✅ 成功导入材质: {best_material}")
            return True
                
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False


def assign_material_to_fbx_objects(material_name="blue black  colour Tiles"):
    """
    将指定名称的材质赋予当前场景中所有FBX导入的Mesh对象
    :param material_name: 要赋予的材质名称
    """
    # 检查材质是否存在
    mat = bpy.data.materials.get(material_name)
    if mat is None:
        print(f"❌ 未找到材质: {material_name}")
        print("💡 尝试智能查找最佳材质...")
        
        # 使用智能材质查找
        best_material = find_best_material()
        if best_material:
            mat = best_material  # 直接使用返回的材质对象
            print(f"✅ 成功找到材质: {best_material.name}")
        else:
            print("❌ 场景中没有可用的材质")
            return False

    # 统计赋材质的对象数量
    assigned_count = 0

    # 遍历所有Mesh对象
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            # 赋予材质
            if obj.data.materials:
                # 替换第一个材质
                obj.data.materials[0] = mat
            else:
                # 没有材质则追加
                obj.data.materials.append(mat)
            assigned_count += 1

    if assigned_count > 0:
        print(f"✅ 已为{assigned_count}个对象赋予材质: {material_name}")
        return True
    else:
        print("⚠️ 没有找到需要赋材质的Mesh对象")
        return False

# ============================================================================
# 主要执行逻辑
# ============================================================================

# 设置文件路径
FBX_FILE_PATH = "/Users/apple/demo_mcp/mmmmccp/Agent_Server_mcp/Agent_server/test_mcp_blender/models/house.fbx"
BLEND_FILE_PATH = "/Users/apple/demo_mcp/mmmmccp/Agent_Server_mcp/Agent_server/test_mcp_blender/material/blue_black.blend"

print("🚀 开始FBX导入和材质设置流程...")

# 1. 导入FBX
success_fbx = simple_import_fbx(FBX_FILE_PATH)
if not success_fbx:
    print("❌ FBX导入失败，终止流程。")
else:
    # 2. 导入材质
    print("🚩 开始导入材质...")
    success_mat = import_material(BLEND_FILE_PATH)
    if not success_mat:
        print("⚠️ 材质导入失败，但FBX已成功导入")
        print("💡 你可以手动导入材质或使用默认材质")
    else:
        # 3. 赋予材质
        print("🚩 开始赋予材质...")
        # 使用智能材质查找，不指定具体名称
        assign_material_to_fbx_objects()

    print("🎬 渲染准备完成！你可以在Blender中渲染场景。")

print("✅ 脚本执行完成！")
