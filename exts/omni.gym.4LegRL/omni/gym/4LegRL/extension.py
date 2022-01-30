import omni.ext
import omni.usd
import omni.ui as ui
import omni.kit.commands
from pxr import Usd, Gf, Tf, Trace
import carb
import carb.events
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
        # self._app = omni.kit.app.get_app()
        # pass
    
    def on_startup(self, ext_id):
        print("[omni.gym.4LegRL] MyExtension startup")

        self.context = omni.usd.get_context()
        self.stage = self.context.get_stage()
        self.selection = self.context.get_selection()
        self.listener = Tf.Notice.Register(Usd.Notice.ObjectsChanged, self._on_change_event, self.stage)

        self._window = ui.Window("My Window", width=300, height=300, dockPreference=ui.DockPreference.RIGHT_BOTTOM)
        with self._window.frame:
            with ui.VStack():
                ui.Label("Select a Prim first")

        def _on_selection_event(e: carb.events.IEvent):
            if e.type==int(omni.usd.StageEventType.SELECTION_CHANGED):
                # print(f"Selection Changed!: %s \n" % str(self.context.get_selection().get_selected_prim_paths()))
                if len(self.context.get_selection().get_selected_prim_paths()) > 1:
                    with self._window.frame:
                        with ui.VStack():
                            ui.Label("Select only one component")
                
                elif len(self.context.get_selection().get_selected_prim_paths()) == 1:
                    with self._window.frame:
                        with ui.VStack():
                            try:
                                self.primSelectedPath = self.context.get_selection().get_selected_prim_paths()[0]
                                self.prim = self.stage.GetPrimAtPath(self.primSelectedPath)
                                self.primRotations = self.prim.GetAttribute('xformOp:rotateXYZ').Get()
                                self.primRotx = self.primRotations[0]
                                self.primRotz = self.primRotations[2]
                            except:
                                print("just wait")

                            ui.Label(f"Prim Selected: '{(self.primSelectedPath)}'")  
                            
                            with ui.HStack():
                                ui.Spacer(height=ui.Percent(10))
                                self.xmodel = ui.SimpleFloatModel(self.primRotx)
                                ui.FloatSlider(self.xmodel, min=-30, max=30)
                                ui.Spacer(height=ui.Percent(20))
                                self.zmodel = ui.SimpleFloatModel(self.primRotz)
                                ui.FloatSlider(self.zmodel, min=-30, max=30)                                
                                ui.Spacer(height=ui.Percent(20))
                
                else:
                    with self._window.frame:
                        with ui.VStack():
                            ui.Label("Select a Prim first")

        self.selection_event_sub = (
            self.context.get_stage_event_stream().create_subscription_to_pop(_on_selection_event, name="Selection")
        )

    @Trace.TraceFunction
    def _on_change_event(self, notice, stage):
        if len(self.context.get_selection().get_selected_prim_paths()) == 1:
            with self._window.frame:
                # self._window.frame.rebuild()
                with ui.VStack():
                    try:
                        self.primSelectedPath = self.context.get_selection().get_selected_prim_paths()[0]
                        self.prim = self.stage.GetPrimAtPath(self.primSelectedPath)
                        self.primRotations = self.prim.GetAttribute('xformOp:rotateXYZ').Get()
                        self.primRotx = self.primRotations[0]
                        self.primRotz = self.primRotations[2]
                    except:
                        print("just wait")

                    ui.Label(f"Prim Selected: '{(self.primSelectedPath)}'")  
                    
                    with ui.HStack():
                        ui.Spacer(height=ui.Percent(10))
                        self.xmodel = ui.SimpleFloatModel(self.primRotx)
                        ui.FloatSlider(self.xmodel, min=-30, max=30)
                        ui.Spacer(height=ui.Percent(20))
                        self.zmodel = ui.SimpleFloatModel(self.primRotz)
                        ui.FloatSlider(self.zmodel, min=-30, max=30)                                
                        ui.Spacer(height=ui.Percent(20))
    
    def on_shutdown(self):
        print("[omni.gym.4LegRL] MyExtension shutdown")