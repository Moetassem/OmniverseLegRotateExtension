import omni.ext
import omni.usd
import omni.ui as ui
import omni.kit.commands
from pxr import Usd, Gf, Tf, Trace
import carb
import carb.events
from .Model import *
import traceback
import asyncio

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class MyExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    
    def __init__(self):
        self.context = None
        self.stage = None
        self.selection = None
        self.xmodel = None
        self.zmodel = None
        # self.app = omni.kit.app.get_app()
        # pass
    
    def on_startup(self, ext_id):
        print("[omni.gym.4LegRL] MyExtension startup")

        self.context = omni.usd.get_context()
        self.stage = self.context.get_stage()
        self.selection = self.context.get_selection()
        self.listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_change_event, self.stage)

        self._window = ui.Window("My Window", width=300, height=300, dockPreference=ui.DockPreference.RIGHT_BOTTOM)
        self.load_window()

        def _on_selection_event(e: carb.events.IEvent):
            if e.type==int(omni.usd.StageEventType.SELECTION_CHANGED):
                self.load_window()
                # print(f"Selection Changed!: %s \n" % str(self.context.get_selection().get_selected_prim_paths()))
                
        self.selection_event_sub = (
            self.context.get_stage_event_stream().create_subscription_to_pop(_on_selection_event, name="Selection")
        )

    def load_window(self):
        if len(self.context.get_selection().get_selected_prim_paths()) > 1:
                with self._window.frame:
                    with ui.VStack():
                        ui.Label("Select only one component")
        
        elif len(self.context.get_selection().get_selected_prim_paths()) == 1:                        
            self.primSelectedPath = self.context.get_selection().get_selected_prim_paths()[0]
            self.xmodel = Model(self.stage, self.primSelectedPath, "x")
            self.zmodel = Model(self.stage, self.primSelectedPath, "z")
        
            def _on_slider_change(self):
                if self.axisIndex == 0:
                    # await omni.kit.app.get_app().next_update_async()
                    omni.kit.commands.execute('ChangePropertyCommand', 
                                        prop_path=self.prim_path+'.xformOp:rotateXYZ', 
                                        value= Gf.Vec3d(self.get_value_as_float(),self.primRots[1],self.primRots[2]),
                                        prev=self.primRots)
                elif self.axisIndex == 2:
                    # await omni.kit.app.get_app().next_update_async()
                    omni.kit.commands.execute('ChangePropertyCommand',
                                        prop_path=self.prim_path+'.xformOp:rotateXYZ', 
                                        value= Gf.Vec3d(self.primRots[0],self.primRots[1],self.get_value_as_float()),
                                        prev=self.primRots)

            self.xmodel.add_value_changed_fn(_on_slider_change)
            self.zmodel.add_value_changed_fn(_on_slider_change)
            
            with self._window.frame:
                with ui.VStack():
                    ui.Label(f"Prim Selected: '{(self.primSelectedPath)}'")
                    
                    with ui.HStack():
                        ui.Spacer(height=ui.Percent(10))
                        ui.FloatSlider(self.xmodel, min=-30, max=30)
                        ui.Spacer(height=ui.Percent(20))
                        ui.FloatSlider(self.zmodel, min=-30, max=30)                     
                        ui.Spacer(height=ui.Percent(20))                                   
        
        else:
            with self._window.frame:
                with ui.VStack():
                    ui.Label("Select a Prim first")
    
    @Trace.TraceFunction
    def _on_change_event(self, notice, stage):
        # await omni.kit.app.get_app().next_update_async()                
        self.load_window()
        
    
    def on_shutdown(self):
        print("[omni.gym.4LegRL] MyExtension shutdown")