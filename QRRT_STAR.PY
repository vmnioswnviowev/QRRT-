# -*- coding: utf-8 -*-

# ==================== 导入库 ====================
# 导入 pygame 库用于图形界面和事件处理
import pygame
# 导入 sys 库用于系统相关操作，如退出程序
import sys

# 从 random 模块导入 randint 函数并重命名为 ri，用于生成随机整数
from random import randint as ri
# 导入 random 模块用于生成随机浮点数
import random
# 从 enum 模块导入 Enum 类，用于定义枚举类型
from enum import Enum
# 导入 os 模块用于目录操作
import os
# 从 datetime 模块导入 datetime 类用于生成时间戳
from datetime import datetime
# 导入 pandas 库用于处理 Excel 文件
import pandas as pd
# 导入 time 模块用于获取更精确的时间
import time

# 创建截图保存目录 - 使用绝对路径确保在正确位置创建
screenshot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "QRRT_screenshots")
os.makedirs(screenshot_dir, exist_ok=True)
print(f"截图目录已设置为: {screenshot_dir}")

# 创建Excel结果保存目录
excel_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "QRRT_results")
os.makedirs(excel_dir, exist_ok=True)
print(f"Excel结果目录已设置为: {excel_dir}")

def save_screenshot(screen, algorithm, state):
    """
    保存屏幕截图到指定目录
    
    Args:
        screen: pygame屏幕对象
        algorithm: 使用的算法名称
        state: 当前状态
    """
    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    filename = f"{screenshot_dir}/{algorithm}_{state}_{timestamp}.png"
    
    try:
        pygame.image.save(screen, filename)
        print(f"截图已保存: {filename}")
        return True
    except Exception as e:
        print(f"保存截图失败: {e}")
        return False

def save_results_to_excel(results_dict):
    """
    保存算法结果到Excel文件，格式便于数据分析和绘图
    
    Args:
        results_dict: 包含算法结果的字典
    """
    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{excel_dir}/QRRT_results_{timestamp}.xlsx"
    
    try:
        # 创建DataFrame
        df = pd.DataFrame([results_dict])
        
        # 保存到Excel文件
        df.to_excel(filename, index=False)
        print(f"结果已保存到Excel: {filename}")
        
        # 同时保存一个累积的结果文件，便于多次运行后的数据比较
        cumulative_filename = f"{excel_dir}/QRRT_cumulative_results.xlsx"
        
        # 检查累积文件是否存在
        if os.path.exists(cumulative_filename):
            # 读取现有文件
            cumulative_df = pd.read_excel(cumulative_filename)
            # 添加新数据
            cumulative_df = pd.concat([cumulative_df, df], ignore_index=True)
        else:
            # 创建新的累积文件
            cumulative_df = df
        
        # 保存累积结果
        cumulative_df.to_excel(cumulative_filename, index=False)
        print(f"累积结果已更新: {cumulative_filename}")
        
        return True
    except Exception as e:
        print(f"保存结果到Excel失败: {e}")
        return False

# ==================== [1] 常量与配置 ====================
# 定义屏幕尺寸常量
SCREEN_WIDTH = 800      # 屏幕宽度为 800 像素 - 增大了屏幕尺寸
SCREEN_HEIGHT = 650     # 屏幕高度为 650 像素 - 增大了屏幕尺寸

# 游戏区域参数定义
GAME_X = 50             # 游戏区域左上角 x 坐标 - 调整了位置
GAME_Y = 50             # 游戏区域左上角 y 坐标 - 调整了位置
GAME_WIDTH = 700        # 游戏区域宽度为 700 像素 - 增大了游戏区域
GAME_HEIGHT = 500       # 游戏区域高度为 500 像素 - 增大了游戏区域
GAME_BORDER = 3         # 游戏区域边框宽度为 3 像素

# 路径优化参数定义
MAX_OPTIMIZATION_ITERATIONS = 500   # 路径优化的最大迭代次数，防止无限循环
MAX_OPTIMIZATION_TIME = 3          # 路径优化的最大时间（秒），控制优化时长

# 颜色定义（RGB 格式）
WHITE = (255, 255, 255)     # 白色
BLACK = (0, 0, 0)           # 黑色
RED = (255, 0, 0)           # 红色
GREEN = (0, 255, 0)         # 绿色
BLUE = (0, 0, 255)          # 蓝色
PATH_COLOR = (20, 200, 20)  # 路径颜色，更亮眼的绿色

# RRT* 算法参数定义
STEP_SIZE = 10          # 扩展步长，控制每次扩展的距离
NODE_RADIUS = 2         # 节点绘制半径（像素）
GOAL_RADIUS = 10        # 起点和终点的绘制半径（像素）
OBSTACLE_RADIUS = 10    # 障碍物绘制半径（像素）

# RRT* 特有参数
REWIRE_RADIUS = 40      # 重连半径，用于寻找邻近节点进行重新连接

# Q-RRT* 新增参数
DEPTH = 2               # 扩展深度，用于Q-RRT*算法中的祖先搜索

# 采样参数
GOAL_SAMPLING_PROBABILITY = 0.05  # 以终点为采样点的概率 (10%)

# UI 元素参数定义
BUTTON_X = 50           # 按钮左上角 x 坐标 - 调整了位置
BUTTON_Y = 600          # 按钮左上角 y 坐标 - 下移到文字下方
BUTTON_WIDTH = 120      # 按钮宽度 - 增大了按钮尺寸
BUTTON_HEIGHT = 40      # 按钮高度 - 调整了按钮尺寸
STATUS_TEXT_Y = 560     # 状态文本 y 坐标 - 放在游戏区域下方

# 游戏状态枚举定义
# 使用枚举类型来表示游戏的不同状态，提高代码可读性和维护性
class GameState(Enum):
    INIT = 0                # 初始化状态
    DRAW_OBSTACLES = 1      # 绘制障碍物状态
    SET_START = 2           # 设置起点状态
    SET_END = 3             # 设置终点状态
    RUNNING_RRT = 4         # 运行 RRT* 算法状态
    PATH_FOUND = 5          # 找到路径状态
    OPTIMIZING_PATH = 6     # 路径优化状态
    QUIT = 7                # 退出状态

# 初始化最终优化时间变量，避免未定义错误
final_optimization_time = 0.0
# 初始化算法开始时间变量
algorithm_start_time = 0.0

# ==================== [2] 类定义 ====================
class Button:
    """一个简单的按钮类，用于处理 UI 中的按钮操作"""
    
    def __init__(self, x, y, width, height, color):
        """
        初始化按钮对象
        :param x: 按钮左上角 x 坐标
        :param y: 按钮左上角 y 坐标
        :param width: 按钮宽度
        :param height: 按钮高度
        :param color: 按钮颜色 (RGB 格式)
        """
        # 创建一个矩形对象来表示按钮的位置和大小
        self.rect = pygame.Rect(x, y, width, height)
        # 设置按钮的颜色
        self.color = color

    def draw(self, screen):
        """
        在屏幕上绘制按钮
        :param screen: pygame 的屏幕对象
        """
        # 使用 pygame.draw.rect 绘制矩形按钮
        pygame.draw.rect(screen, self.color, self.rect)

    def is_clicked(self, pos):
        """
        检查按钮是否被点击
        :param pos: 鼠标点击位置 (x, y)
        :return: 如果点击位置在按钮矩形内返回 True，否则返回 False
        """
        # 使用 collidepoint 方法检查点击位置是否在按钮矩形内
        return self.rect.collidepoint(pos)

# ==================== [3] 辅助函数 ====================
def is_point_in_game_area(x, y):
    """
    检查点是否在有效的游戏区域内
    :param x: 点的 x 坐标
    :param y: 点的 y 坐标
    :return: 如果点在游戏区域内返回 True，否则返回 False
    """
    # 检查 x 和 y 坐标是否在游戏区域内（不包括边框）
    return (GAME_X < x < GAME_X + GAME_WIDTH and
            GAME_Y < y < GAME_Y + GAME_HEIGHT)

def get_random_point_in_game_area():
    """
    在游戏区域内生成一个随机点
    :return: 随机点坐标 (x, y)
    """
    # 在游戏区域内部（避开边框）生成随机坐标
    x_random = ri(GAME_X + GAME_BORDER, GAME_X + GAME_WIDTH - GAME_BORDER - 1)
    y_random = ri(GAME_Y + GAME_BORDER, GAME_Y + GAME_HEIGHT - GAME_BORDER - 1)
    return (x_random, y_random)

def get_distance(p1, p2):
    """
    计算两点之间的欧几里得距离
    :param p1: 第一个点 (x, y)
    :param p2: 第二个点 (x, y)
    :return: 两点之间的欧几里得距离
    """
    # 使用欧几里得距离公式计算两点间距离: sqrt((x2-x1)^2 + (y2-y1)^2)
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5

def get_line_points(p1, p2):
    """
    获取两点之间连线上的所有整数坐标点 (Bresenham's line algorithm 实现)
    :param p1: 起点 (x, y)
    :param p2: 终点 (x, y)
    :return: 连线上的所有整数坐标点列表
    """
    # 初始化起点和终点坐标
    x1, y1 = p1
    x2, y2 = p2
    # 初始化点列表
    points = []
    # 计算 x 和 y 方向的增量
    dx, dy = abs(x2 - x1), -abs(y2 - y1)
    # 确定 x 和 y 方向的步长（1 或 -1）
    sx, sy = 1 if x1 < x2 else -1, 1 if y1 < y2 else -1
    # 初始化误差项
    err = dx + dy
    # 循环直到到达终点
    while True:
        # 将当前点添加到列表中
        points.append((x1, y1))
        # 如果到达终点则退出循环
        if x1 == x2 and y1 == y2:
            break
        # 计算误差的两倍
        e2 = 2 * err
        # 根据误差调整 x 坐标
        if e2 >= dy:
            err += dy
            x1 += sx
        # 根据误差调整 y 坐标
        if e2 <= dx:
            err += dx
            y1 += sy
    return points

# RRT* 新增：独立的碰撞检测函数
def is_collision_free(p1, p2, obstacles):
    """
    检查两点之间的路径是否无碰撞（即路径上没有障碍物）
    :param p1: 起点 (x, y)
    :param p2: 终点 (x, y)
    :param obstacles: 障碍物列表，每个障碍物是一个坐标点 (x, y)
    :return: 如果路径无碰撞返回 True，否则返回 False
    """
    # 获取两点之间连线上的所有整数坐标点
    path_points = get_line_points(p1, p2)
    # 遍历路径上的每个点
    for p in path_points:
        # 确保检测点在屏幕内
        if not (0 <= p[0] < SCREEN_WIDTH and 0 <= p[1] < SCREEN_HEIGHT):
            return False
        # 检查该点是否与任何障碍物重合或足够接近
        for obstacle in obstacles:
            if get_distance(p, obstacle) < OBSTACLE_RADIUS:
                return False
    # 如果路径上所有点都不是障碍物，则无碰撞
    return True

# Q-RRT* 辅助函数：获取节点的祖先集合
def ancestry(node, depth, parent_map):
    """
    获取节点及其指定深度的祖先节点集合
    :param node: 当前节点
    :param depth: 搜索深度
    :param parent_map: 父节点映射表
    :return: 节点及其祖先的集合列表
    """
    ancestors = []
    current = node
    for _ in range(depth + 1):  # +1 包含节点本身
        if current is None:
            break
        if current not in ancestors:  # 避免重复添加
            ancestors.append(current)
        current = parent_map.get(current)
    return ancestors

# Q-RRT* 辅助函数：更新节点及其所有子节点的成本
def update_descendant_costs(node, cost_map, parent_map):
    """
    更新节点及其所有子节点的成本
    :param node: 要更新的起始节点
    :param cost_map: 成本映射表
    :param parent_map: 父节点映射表
    """
    # 找到当前节点的所有子节点
    children = [child for child, parent in parent_map.items() if parent == node]
    
    # 对于每个子节点，更新其成本并递归更新其子节点
    for child in children:
        # 计算子节点的新成本（父节点成本 + 父节点到子节点的距离）
        new_child_cost = cost_map[node] + get_distance(node, child)
        # 如果子节点成本发生变化，则更新并递归
        if abs(new_child_cost - cost_map[child]) > 1e-6:  # 避免浮点精度问题
            cost_map[child] = new_child_cost
            # 递归更新子节点的子节点
            update_descendant_costs(child, cost_map, parent_map)

# Q-RRT* 核心算法
def run_rrt_star_step(parent_map, cost_map, target_point, step_size, rewire_radius, obstacles, start_node, end_node):
    """
    执行单步 RRT* 扩展算法
    :param parent_map: 存储树结构的字典，键为节点坐标，值为其父节点坐标
    :param cost_map: 存储节点成本的字典，键为节点坐标，值为从起点到该节点的成本
    :param target_point: 随机采样点 (x, y)
    :param step_size: 扩展步长
    :param rewire_radius: 重连半径
    :param obstacles: 障碍物列表
    :param start_node: 起点坐标
    :param end_node: 终点坐标
    :return: (is_success, new_node) 是否成功扩展及新节点坐标
    """
    # 1. 寻找最近的节点
    # 在现有树中找到距离目标点最近的节点
    nearest_node = min(parent_map.keys(), key=lambda p: get_distance(p, target_point))

    # 2. 计算朝向目标点的方向向量并归一化
    # 计算从最近节点指向目标点的方向向量
    direction = (target_point[0] - nearest_node[0], target_point[1] - nearest_node[1])
    # 计算最近节点与目标点之间的距离
    dist = get_distance(target_point, nearest_node)
    # 如果距离为 0，说明两点重合，无法扩展，返回失败
    if dist == 0:
        return False, None

    # 3. 生成新节点
    # 沿着方向向量，从最近节点开始，按照步长生成新节点
    new_node = (int(nearest_node[0] + direction[0] / dist * step_size),
                int(nearest_node[1] + direction[1] / dist * step_size))

    # 检查新节点是否在游戏区域内以及是否已经在树中
    # 如果新节点不在游戏区域内或已经在树中，则此次扩展失败
    if not is_point_in_game_area(new_node[0], new_node[1]) or new_node in parent_map:
        return False, None

    # 4. 在邻域内为新节点选择最佳父节点（Q-RRT* 改进）
    # 找到所有在重连半径内的邻近节点
    neighbors = [node for node in parent_map if get_distance(node, new_node) < rewire_radius]
    
    # 如果邻域为空，则使用最近的节点作为候选
    if not neighbors:
        neighbors.append(nearest_node)
        
    # 初始化最佳父节点为最近节点，最小成本为从最近节点到达新节点的总成本
    best_parent = nearest_node
    min_cost = cost_map[nearest_node] + get_distance(nearest_node, new_node)

    # 遍历所有邻近节点及其祖先，寻找成本最低的父节点（Q-RRT* 改进）
    for neighbor in neighbors:
        # 获取邻近节点及其DEPTH代祖先
        candidates = ancestry(neighbor, DEPTH, parent_map)
        
        for candidate in candidates:
            # 计算从该候选节点到达新节点的总成本
            cost = cost_map[candidate] + get_distance(candidate, new_node)
            # 如果成本更低且路径无碰撞，则更新最佳父节点
            if cost < min_cost and is_collision_free(candidate, new_node, obstacles):
                min_cost = cost
                best_parent = candidate
            
    # 如果从最佳父节点到新节点的路径有障碍，则此次扩展失败
    if not is_collision_free(best_parent, new_node, obstacles):
        return False, None

    # 5. 将新节点添加到树中
    # 设置新节点的父节点
    parent_map[new_node] = best_parent
    # 记录新节点的成本
    cost_map[new_node] = min_cost

    # 6. Rewire: 重连邻域内的节点（Q-RRT* 改进）
    # 遍历所有邻近节点及其祖先，尝试通过新节点或其父节点重连
    for neighbor in neighbors:
        # 获取邻近节点及其DEPTH代祖先
        rewire_candidates = ancestry(neighbor, DEPTH, parent_map)
        
        for candidate in rewire_candidates:
            # 不重连新节点的父节点（避免无效操作）
            if candidate == best_parent:
                continue
            
            # 计算通过新节点到达候选节点的新潜在成本
            new_potential_cost = cost_map[new_node] + get_distance(new_node, candidate)
            # 如果新潜在成本更低且路径无碰撞，则进行重连
            if new_potential_cost < cost_map[candidate] and is_collision_free(new_node, candidate, obstacles):
                # 更新候选节点的父节点为新节点
                parent_map[candidate] = new_node
                # 更新候选节点的成本
                cost_map[candidate] = new_potential_cost
                # 递归更新候选节点的所有子节点的成本
                update_descendant_costs(candidate, cost_map, parent_map)
            
            # 额外尝试通过新节点的父节点进行重连（Q-RRT* 改进）
            if best_parent is not None:
                new_parent_potential_cost = cost_map[best_parent] + get_distance(best_parent, candidate)
                if (new_parent_potential_cost < cost_map[candidate] and 
                    candidate != best_parent and 
                    is_collision_free(best_parent, candidate, obstacles)):
                    # 更新候选节点的父节点为新节点的父节点
                    parent_map[candidate] = best_parent
                    # 更新候选节点的成本
                    cost_map[candidate] = new_parent_potential_cost
                    # 递归更新候选节点的所有子节点的成本
                    update_descendant_costs(candidate, cost_map, parent_map)
    
    # 扩展成功，返回新节点
    return True, new_node

# 重绘整个场景
def redraw_scene(screen, obstacles, parent_map, start_node, end_node, game_state):
    """
    重新绘制整个场景
    :param screen: pygame 屏幕对象
    :param obstacles: 障碍物列表
    :param parent_map: 树结构字典
    :param start_node: 起点坐标
    :param end_node: 终点坐标
    :param game_state: 当前游戏状态
    """
    # 填充背景色为白色
    screen.fill(WHITE)
    
    # 绘制游戏区域边框
    pygame.draw.rect(screen, BLACK, (GAME_X, GAME_Y, GAME_WIDTH, GAME_HEIGHT), GAME_BORDER)
    
    # 绘制所有障碍物
    for obstacle in obstacles:
        pygame.draw.circle(screen, BLACK, obstacle, OBSTACLE_RADIUS)
    
    # 绘制起点和终点（如果已设置）
    if start_node:
        pygame.draw.circle(screen, RED, start_node, GOAL_RADIUS)
    if end_node:
        pygame.draw.circle(screen, GREEN, end_node, GOAL_RADIUS)
    
    # 绘制 RRT* 树（如果正在运行算法）
    if game_state in [GameState.RUNNING_RRT, GameState.PATH_FOUND, GameState.OPTIMIZING_PATH, GameState.QUIT]:
        for node in parent_map:
            if parent_map[node] is not None:
                pygame.draw.line(screen, BLUE, node, parent_map[node], 1)
                pygame.draw.circle(screen, BLUE, node, NODE_RADIUS)
        
        # 如果找到路径，绘制路径（在PATH_FOUND及之后状态绘制）
        if game_state in [GameState.PATH_FOUND, GameState.OPTIMIZING_PATH, GameState.QUIT] and end_node and end_node in parent_map:
            current = end_node
            while current != start_node:
                parent = parent_map.get(current)
                if parent:
                    pygame.draw.line(screen, PATH_COLOR, current, parent, 3)
                    current = parent
                else:
                    break

# ==================== [4] 绘图函数 ====================
def draw_ui(screen, font, button, reset_button, status_text):
    """
    绘制所有UI元素
    :param screen: pygame 的屏幕对象
    :param font: pygame 的字体对象
    :param button: 按钮对象
    :param reset_button: 重置按钮对象
    :param status_text: 状态文本内容
    """
    # 1. 绘制状态描述文本 - 放在游戏区域下方
    # 计算文本区域的最大宽度，确保不超出屏幕边界
    max_text_width = SCREEN_WIDTH - 2 * BUTTON_X  # 使用整个屏幕宽度减去两边边距
    
    # 先用白色矩形覆盖旧文本区域，实现刷新效果
    pygame.draw.rect(screen, WHITE, (BUTTON_X, STATUS_TEXT_Y - 5, max_text_width, 30))
    
    # 渲染完整的状态文本，不进行截断
    status_surf = font.render(status_text, True, BLACK)
    
    # 获取文本矩形并设置位置 - 放在游戏区域下方居中
    status_rect = status_surf.get_rect(center=(SCREEN_WIDTH // 2, STATUS_TEXT_Y + 10))
    screen.blit(status_surf, status_rect)
    
    # 2. 绘制按钮和按钮文本 - 放在文字下方
    button.draw(screen)
    # 渲染模式按钮文本
    btn_text_surf = font.render('CLICK HERE', True, WHITE)
    # 获取文本矩形并居中显示在按钮上
    btn_text_rect = btn_text_surf.get_rect(center=button.rect.center)
    screen.blit(btn_text_surf, btn_text_rect)
    
    # 3. 绘制重置按钮
    pygame.draw.rect(screen, reset_button.color, reset_button.rect)
    pygame.draw.rect(screen, WHITE, reset_button.rect, 2)  # 白色边框
    # 绘制重置按钮文本
    reset_text_surf = font.render('RESET', True, WHITE)
    reset_text_rect = reset_text_surf.get_rect(center=reset_button.rect.center)
    screen.blit(reset_text_surf, reset_text_rect)


# ==================== [5] 主函数 ====================
def main():
    """
    程序主入口函数
    """
    # 初始化 pygame 库
    pygame.init()

    # 初始化屏幕和字体
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("RRT* Path Planning Visualization")
    font = pygame.font.SysFont('segoeuisemibold', 16)
    
    # 初始化时钟对象，用于控制帧率
    clock = pygame.time.Clock()
    
    # 路径优化计时器和计数器
    optimization_start_time = 0     # 优化开始时间
    optimization_iterations = 0     # 优化迭代次数
    global algorithm_start_time     # 使用全局变量记录算法开始时间
    
    # 初始化状态和数据结构
    game_state = GameState.DRAW_OBSTACLES  # 直接从绘制障碍物状态开始
    start_node = None               # 起点坐标
    end_node = None                 # 终点坐标
    parent_map = {}                 # 存储树结构的字典
    cost_map = {}                   # RRT* 新增：存储节点成本的字典
    obstacles = []                  # 存储障碍物坐标的列表
    current_path_length = float('inf')  # 当前路径长度
    path_found_time = 0.0           # 找到初始路径的时间

    # 创建UI元素 - 参考comparison_10_14_time_excel_4_5的布局方式
    mode_button = Button(BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, BLACK)
    # 创建重置按钮，位置在模式按钮右侧但不与文字重叠
    reset_button = Button(BUTTON_X + BUTTON_WIDTH + 20, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, RED)

    # 主循环
    running = True
    while running:

        # 事件处理循环
        for event in pygame.event.get():
            # 处理退出事件
            if event.type == pygame.QUIT:
                running = False
            
            # 处理鼠标点击事件
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                
                # 重置按钮点击检测
                if reset_button.is_clicked(mouse_pos):
                    # 重置所有必要的变量和状态到初始状态
                    print("程序已完全重置")
                    game_state = GameState.DRAW_OBSTACLES
                    start_node = None
                    end_node = None
                    parent_map = {}
                    cost_map = {}
                    obstacles = []
                    current_path_length = float('inf')
                    # 重置优化参数
                    optimization_start_time = 0
                    optimization_iterations = 0
                    print("可以重新开始绘制障碍物")
                
                # 点击按钮 -> 切换状态
                elif mode_button.is_clicked(mouse_pos):
                    # 根据当前状态切换到下一个状态
                    if game_state == GameState.DRAW_OBSTACLES:
                        game_state = GameState.SET_START
                    elif game_state == GameState.SET_START and start_node:
                        game_state = GameState.SET_END
                    elif game_state == GameState.SET_END and end_node:
                        game_state = GameState.RUNNING_RRT
                    # 添加重新开始功能：当算法完成或退出状态时，重新开始路径规划
                    elif game_state in [GameState.QUIT, GameState.PATH_FOUND, GameState.OPTIMIZING_PATH]:
                            if start_node and end_node:
                                print("重新开始路径规划...")
                                # 重置算法相关数据结构，但保留障碍物、起点和终点
                                parent_map = {start_node: None}  # 重新初始化父节点映射，保留起点
                                cost_map = {start_node: 0}      # 重新初始化成本映射，保留起点成本
                                # 重置优化参数
                                optimization_start_time = 0
                                optimization_iterations = 0
                                # 重置路径长度
                                current_path_length = float('inf')
                                # 重置路径找到时间
                                path_found_time = 0.0
                                # 记录算法开始时间
                                algorithm_start_time = time.time()
                            # 添加调试信息输出
                            print(f"重置完成 - 树节点数量: {len(parent_map)}, 障碍物数量: {len(obstacles)}, 起点: {start_node}, 终点: {end_node}")
                            # 切换到运行状态
                            game_state = GameState.RUNNING_RRT
                            print(f"当前状态切换为: {game_state}")
                
                # 在游戏区域内点击
                elif is_point_in_game_area(mouse_pos[0], mouse_pos[1]):
                    # 根据当前状态处理点击事件
                    if game_state == GameState.SET_START and not start_node:
                        # 设置起点
                        start_node = mouse_pos
                        parent_map[start_node] = None  # 起点没有父节点
                        cost_map[start_node] = 0      # RRT* 新增：起点成本为0
                    elif game_state == GameState.SET_END and not end_node:
                        # 设置终点
                        end_node = mouse_pos

        # 鼠标拖拽事件 (用于画障碍物)
        if game_state == GameState.DRAW_OBSTACLES:
            # 检查鼠标左键是否按住
            mouse_pressed = pygame.mouse.get_pressed()
            if mouse_pressed[0]:  # 如果左键按住
                mouse_pos = pygame.mouse.get_pos()
                # 如果鼠标在游戏区域内，则添加障碍物
                if is_point_in_game_area(mouse_pos[0], mouse_pos[1]):
                    # 避免重复添加相同位置的障碍物
                    obstacle_exists = False
                    for obstacle in obstacles:
                        if get_distance(obstacle, mouse_pos) < OBSTACLE_RADIUS:
                            obstacle_exists = True
                            break
                    if not obstacle_exists:
                        obstacles.append(mouse_pos)

        # ==================== 状态机逻辑 ====================
        # 根据当前状态设置相应的状态消息
        status_message = ""

        
        if game_state == GameState.DRAW_OBSTACLES:
            # 绘制障碍物状态
            mode_button.color = BLACK
            status_message = "Draw obstacles, then click the button."
        
        elif game_state == GameState.SET_START:
            # 设置起点状态
            mode_button.color = RED
            status_message = "Set the START point (red), then click the button."

        elif game_state == GameState.SET_END:
            # 设置终点状态
            mode_button.color = GREEN
            status_message = "Set the END point (green), then click the button."

        elif game_state == GameState.RUNNING_RRT:
            # 运行 RRT* 算法状态
            mode_button.color = BLUE
            status_message = "Exploring path using RRT*..."
            
            # 如果是第一次进入该状态，记录开始时间
            if len(parent_map) == 1:  # 只有起点的情况
                algorithm_start_time = time.time()
            
            # 多次迭代以加快速度
            for _ in range(5):
                # 生成随机点，有GOAL_SAMPLING_PROBABILITY几率直接以终点作为采样点
                if random.random() < GOAL_SAMPLING_PROBABILITY:
                    rand_point = end_node  # 直接使用终点作为采样点
                else:
                    rand_point = get_random_point_in_game_area()  # 随机生成采样点
                # 执行一步 RRT* 扩展
                success, new_node = run_rrt_star_step(parent_map, cost_map, rand_point, STEP_SIZE, REWIRE_RADIUS, obstacles, start_node, end_node)
                
                # 检查是否到达终点区域
                if success and get_distance(new_node, end_node) < GOAL_RADIUS:
                    # 检查从新节点到终点的路径是否无碰撞
                    if is_collision_free(new_node, end_node, obstacles):
                        # 将终点添加到树中
                        parent_map[end_node] = new_node
                        cost_map[end_node] = cost_map[new_node] + get_distance(new_node, end_node)
                        current_path_length = cost_map[end_node]
                        # 记录找到路径的时间
                        path_found_time = time.time() - algorithm_start_time
                        print(f"找到路径！路径长度: {current_path_length:.2f}, 耗时: {path_found_time:.2f}秒")

                        game_state = GameState.PATH_FOUND
                        break  # 退出RRT运行

        elif game_state == GameState.PATH_FOUND:
            # 找到路径状态
            status_message = f"Path found! Path length: {current_path_length:.2f}, Now optimizing..."
            # 先重绘场景确保路径可见
            redraw_scene(screen, obstacles, parent_map, start_node, end_node, game_state)
            draw_ui(screen, font, mode_button, reset_button, status_message)
            # 更新显示确保路径渲染完成
            pygame.display.flip()
            # 短暂延迟确保渲染完成
            pygame.time.delay(100)
            # 保存初始路径截图
            save_screenshot(screen, "QRRT", "initial_path_found")
            game_state = GameState.OPTIMIZING_PATH
            # 初始化优化参数
            optimization_start_time = pygame.time.get_ticks() / 1000.0  # 转换为秒
            optimization_iterations = 0


        elif game_state == GameState.OPTIMIZING_PATH:
            # 路径优化状态
            # 计算已经优化的时间
            current_time = pygame.time.get_ticks() / 1000.0
            elapsed_time = current_time - optimization_start_time
            
            # 检查是否达到优化限制
            if optimization_iterations >= MAX_OPTIMIZATION_ITERATIONS or elapsed_time >= MAX_OPTIMIZATION_TIME:
                # 记录最终优化时间，确保后续显示固定
                final_optimization_time = elapsed_time
                # 计算总运行时间
                total_time = path_found_time + final_optimization_time
                status_message = f"Optimization complete! Iterations: {optimization_iterations}, Time: {final_optimization_time:.2f}s, Final path length: {current_path_length:.2f}"
                # 先重绘场景确保路径可见
                redraw_scene(screen, obstacles, parent_map, start_node, end_node, game_state)
                draw_ui(screen, font, mode_button, reset_button, status_message)
                # 更新显示确保路径渲染完成
                pygame.display.flip()
                # 短暂延迟确保渲染完成
                pygame.time.delay(100)
                # 保存优化后路径截图
                save_screenshot(screen, "QRRT", "path_optimized")
                
                # 准备保存到Excel的结果数据
                results = {
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'algorithm': 'Q-RRT*',
                    'obstacle_count': len(obstacles),
                    'node_count': len(parent_map),
                    'initial_path_length': current_path_length,
                    'final_path_length': current_path_length,  # 在这个实现中，初始和最终可能相同
                    'path_found_time': path_found_time,
                    'optimization_time': final_optimization_time,
                    'total_time': total_time,
                    'optimization_iterations': optimization_iterations,
                    'step_size': STEP_SIZE,
                    'rewire_radius': REWIRE_RADIUS,
                    'depth': DEPTH
                }
                
                # 保存结果到Excel
                save_results_to_excel(results)
                
                game_state = GameState.QUIT
            else:

                # 继续优化路径
                optimization_iterations += 1
                
                # 执行RRT*优化步骤
                for _ in range(5):  # 每帧执行3次优化
                    # 生成随机点，有GOAL_SAMPLING_PROBABILITY几率直接以终点作为采样点
                    if random.random() < GOAL_SAMPLING_PROBABILITY:
                        rand_point = end_node  # 直接使用终点作为采样点
                    else:
                        rand_point = get_random_point_in_game_area()  # 随机生成采样点
                    success, new_node = run_rrt_star_step(parent_map, cost_map, rand_point, STEP_SIZE, REWIRE_RADIUS, obstacles, start_node, end_node)
                
                # 检查路径是否更新
                if end_node in cost_map and cost_map[end_node] < current_path_length:
                    current_path_length = cost_map[end_node]
                    print(f"路径更新！新路径长度: {current_path_length:.2f}")
                
                status_message = f"Optimizing path... Iteration: {optimization_iterations}, Time: {elapsed_time:.2f}s, Path length: {current_path_length:.2f}"
        
        elif game_state == GameState.QUIT:
             # 退出状态 - 保持显示优化完成的消息
             # 使用之前记录的固定最终优化时间
             status_message = f"Optimization complete! Iterations: {optimization_iterations}, Time: {final_optimization_time:.2f}s, Final path length: {current_path_length:.2f}"

        # 重新绘制整个场景
        redraw_scene(screen, obstacles, parent_map, start_node, end_node, game_state)
        
        # 绘制UI和更新屏幕
        draw_ui(screen, font, mode_button, reset_button, status_message)
        pygame.display.update()

    # 退出游戏
    pygame.quit()
    sys.exit()


# 程序入口点
if __name__ == '__main__':
    main()