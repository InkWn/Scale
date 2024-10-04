import tkinter as tk


# 自定义滑块
class InkWnScale(tk.Canvas):
    def __init__(
            self, master,
            variable: tk.IntVar | tk.DoubleVar,
            length: int = 150, height: int = 5,
            scale_width: int = 15, scale_height: int = 20,
            show_value: bool = True, font: tuple = (None, 10), fg: str = "black", padx: int = 10,
            line_bg: str = "white", select_bg: str = "red",
            rect_bg: str = "#CDCDCD", focus_bg: str = "#A6A6A6", click_bg: str = "#606060",
            from_=0, to=100, precision: int = 0,
            wheel_step: int | float = 1,
            command=None,
    ):
        """
        :param master: 父窗口
        :param variable: 绑定变量
        :param length: 直线长度
        :param height: 直线高度
        :param scale_width: 滑块宽度
        :param scale_height: 滑块高度，且决定画布的高度
        :param show_value: 是否显示值
        :param font: 字体，show_value=True时生效
        :param fg: 字体颜色，show_value=True时生效
        :param padx: 文字与直线的距离，show_value=True时生效
        :param line_bg: 直线背景色
        :param select_bg: 经过的背景色
        :param rect_bg: 滑块背景色
        :param focus_bg: 焦距背景色
        :param click_bg: 点击背景色
        :param from_: 起始值
        :param to:  结束值
        :param precision: 精度，小数点后几位
        :param wheel_step: 鼠标滚动加减的步长
        :param command: 绑定事件
        """
        super().__init__(master)
        self.config(height=scale_height, bg=master["bg"], highlightthickness=0)
        if show_value:
            text_length = max(len(str(from_)), len(str(to))) + precision  # 文本长度
            self.config(width=length + font[1] * text_length + padx)
        else: self.config(width=length)
        # 参数
        self.variable = variable
        self.length = length
        self.height = height
        self.scale_width = scale_width
        self.scale_height = scale_height
        self.show_value = show_value
        self.line_bg = line_bg
        self.select_bg = select_bg
        self.rect_bg = rect_bg
        self.focus_bg = focus_bg
        self.click_bg = click_bg
        self.from_ = from_
        self.to = to
        self.precision = precision
        self.wheel_step = wheel_step
        self.command = command
        # 变量
        self.InCanvas = False   # 是否在画布上
        self.Click = False      # 是否点击
        self.InRect = False     # 是否在矩形区域
        # 滑块参数
        self.rectangle_line_height_range = (
                (self.scale_height - self.height) // 2,
                (self.scale_height - self.height) // 2 + self.height
        )  # 直线高度范围
        value_get = self.variable.get()
        pos_x = (value_get - self.from_) / (self.to - self.from_) * (self.length - self.scale_width)
        # 直线
        self.create_rectangle(
            0, self.rectangle_line_height_range[0], self.length, self.rectangle_line_height_range[1],
            fill=self.line_bg, width=0
        )
        # 选中区域
        self.rectagnle_selection = self.create_rectangle(
            0, self.rectangle_line_height_range[0], pos_x, self.rectangle_line_height_range[1],
            fill=self.select_bg, width=0
        )
        # 滑块
        self.rectangle_scale = self.create_rectangle(
            pos_x, 0, self.scale_width + pos_x, self.scale_height,
            fill=self.rect_bg, width=0
        )
        # 显示值
        if show_value:
            self.text_value = self.create_text(
                self.length + padx, self.scale_height // 2, anchor="w",
                text=f"{value_get:.{self.precision}f}", font=font, fill=fg,
            )
        # 绑定事件
        self.bind("<Enter>", self.__enter)  # 鼠标进入
        self.bind_all("<Motion>", self.__move)  # 鼠标移动
        self.bind("<Leave>", self.__leave)  # 鼠标离开
        self.bind("<Button-1>", self.__click)  # 鼠标点击
        self.bind("<ButtonRelease-1>", self.__release)  # 鼠标释放
        self.bind("<MouseWheel>", self.__wheel)  # 鼠标滚动
        self.bind("<Destroy>", self.__destroy)  # 销毁
        # 绑定variable是否发生变化
        self.variable.trace_add("write", self.__bind_value)

    # 关闭
    def __destroy(self, event):
        _ = event
        self.unbind_all("<Enter>")
        self.unbind_all("<Motion>")
        self.unbind_all("<Leave>")
        self.unbind_all("<Button-1>")
        self.unbind_all("<ButtonRelease-1>")
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Destroy>")

    # 鼠标进入
    def __enter(self, event):
        _ = event
        self.InCanvas = True

    # 鼠标移动
    def __move(self, event):
        if not self.InCanvas: return  # 鼠标未进入画布
        if self.Click:
            self.__update(event.x)
        else:
            pos_1, pos_2, pos_3, pos_4 = self.coords(self.rectangle_scale)
            if pos_1 <= event.x <= pos_3 and pos_2 <= event.y <= pos_4:
                self.InRect = True
                self.itemconfig(self.rectangle_scale, fill=self.focus_bg)
            else:
                self.InRect = False
                self.itemconfig(self.rectangle_scale, fill=self.rect_bg)

    # 鼠标离开
    def __leave(self, event):
        _ = event
        if not self.Click:
            self.InRect = False
            self.InCanvas = False
            self.itemconfig(self.rectangle_scale, fill=self.rect_bg)

    # 鼠标点击
    def __click(self, event):
        _ = event
        self.Click = True
        if self.InRect:
            self.itemconfig(self.rectangle_scale, fill=self.click_bg)
            self.config(cursor="sb_h_double_arrow")
        else:
            if self.InCanvas:
                self.__update(event.x)

    # 鼠标释放
    def __release(self, event):
        _ = event
        if self.Click:
            self.Click = False
            self.itemconfig(self.rectangle_scale, fill=self.focus_bg)
            self.config(cursor="")

    # 鼠标滚动
    def __wheel(self, event):
        if not self.InCanvas: return
        value = self.variable.get()
        if event.delta > 0:   # 向上滚动
            value += self.wheel_step
        else:   # 向下滚动
            value -= self.wheel_step
        pos_x = (value - self.from_) / (self.to - self.from_) * (self.length - self.scale_width)
        self.__update(pos_x)

    # 绑定variable是否变化
    def __bind_value(self, *args):
        _ = args
        value = self.variable.get()
        pos_x = (value - self.from_) / (self.to - self.from_) * (self.length - self.scale_width)
        self.__update(pos_x)

    # 更新滑块与选中区域
    def __update(self, pos_x):
        pos_x = max(0, min(self.length - self.scale_width, pos_x))  # 限制滑块位置在直线内
        self.coords(
            self.rectangle_scale,
            pos_x, 0,
            pos_x + self.scale_width, self.scale_height
        )
        self.coords(
            self.rectagnle_selection,
            0, self.rectangle_line_height_range[0],
            pos_x, self.rectangle_line_height_range[1]
        )
        Percen = (pos_x / (self.length - self.scale_width))
        value = round(self.from_ + (self.to - self.from_) * Percen, self.precision)  # 计算滑块位置对应的数值
        self.variable.set(value)
        if self.show_value:
            # 改变显示值
            self.itemconfig(
                self.text_value,
                text=f"{self.variable.get():.{self.precision}f}",
            )
        if self.command is not None: self.command()


if __name__ == '__main__':
    from tkinter import ttk
    root = tk.Tk()
    root.geometry("300x160")
    var = tk.DoubleVar(value=0)
    scale1 = InkWnScale(root, variable=var, from_=0, to=255, precision=0, show_value=True)
    scale1.pack(side="top", pady=10)
    scale2 = tk.Scale(root, variable=var, from_=0, to=255, orient=tk.HORIZONTAL, length=150,)
    scale2.pack(side="top", pady=10)
    scale3 = ttk.Scale(root, variable=var, from_=0, to=255, orient=tk.HORIZONTAL, length=150,)
    scale3.pack(side="top", pady=10)
    root.mainloop()
