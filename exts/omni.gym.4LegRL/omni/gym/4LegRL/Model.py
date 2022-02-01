import omni.ui as ui

class Model(ui.SimpleFloatModel):
    def __init__(self, stage, prim_path: str, axis: str):
        axes = ['x', 'y', 'z']
        if axis not in axes:
            raise ValueError("Invalid sim type. Expected one of: %s" % axes)
        self.stage = stage
        self.prim_path = prim_path
        self.axis = axis
        self.axisIndex = axes.index(axis)
        self.prim = self.stage.GetPrimAtPath(self.prim_path)
        self.primRots = self.prim.GetAttribute('xformOp:rotateXYZ').Get()
        super().__init__(self.primRots[self.axisIndex])

    def getAxisIndex(self):
        return self.axisIndex

    def getPrimPath(self):
        return self.prim_path

    # def setPrimPath(self, new_prim_path: str):
    #     _value_changed()
    #     self.prim_path = new_prim_path

    def _value_changed(self) -> None:
        return super()._value_changed()