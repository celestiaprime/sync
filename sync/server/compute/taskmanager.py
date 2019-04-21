import logging
from concurrent.futures import ThreadPoolExecutor, Future
from .models import NSTModel, AdaInModel
from ..ServerComputedImage import ServerComputedImage
import asyncio
logger = logging.getLogger(__name__)


class TaskManager:
    def __init__(self, data_manager):
        self.models = {'nst': NSTModel(), 'adain': AdaInModel()} 
        self.executor = ThreadPoolExecutor()
        self.data_manager = data_manager
        self.tasks = {}
        self.loop = asyncio.get_event_loop()

    def compute(self, image, inputs):
        assert isinstance(image, ServerComputedImage) 
        model_key = image.params['model_key']
        logger.info('Computing with model {}...'.format(model_key))
        print(self.models[model_key])
        
        image_data = self.models[model_key].run(inputs)
        logger.info('Done computing!')
        return image_data
        #image.update_data(image_data)
        
    async def schedule_compute(self, image):
        assert isinstance(image, ServerComputedImage) 
        logger.info("scheduling delayed compute...")
        try:
            await asyncio.sleep(5)  # Give other executions a chance to cancel this this one
            
            logger.info('Computing...')
            
            inputs = {}
            input_slots = image.get_slots()

            for slot, input_image in input_slots.items():
                try:
                    inputs[slot] = input_image.get_image()
                except:
                    inputs[slot] = input_image
            
            data = await self.loop.run_in_executor(self.executor, self.compute, image, inputs)
                
        except asyncio.CancelledError:
            logger.warn('Compute aborted')
            raise
        except Exception as e:
            logger.exception(e)
            raise
        
        try:
            logger.info("Handling computed data...")
            if (data == image.get_image()).all():
                logger.error("Computed data is the same as stored data!")
                #import ipdb 
                #ipdb.set_trace()
            await asyncio.shield(image.update_data(data))

        except asyncio.CancelledError:
            logger.error('Compute aborted during data handling!')            
    
    

    
    async def compute_debounce(self, image):
        if image in self.tasks:
            status = self.tasks[image].cancel() # Cancel other executions of schedule_compute
            if status == False:
                logger.warn('Computation cancel failed. The task is (probably) completed.')
                
        try:
            await self.tasks[image]
        except:
            pass

        self.tasks[image] = asyncio.ensure_future(self.schedule_compute(image)) # Defer to the actual function
            



    def listen(self, data_manager):
        pass