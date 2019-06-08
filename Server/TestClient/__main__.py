from .test_client import *
import asyncio

classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
test_classes = {}

for name, value in classes:
    if issubclass(value, DefaultTest):
        test_classes[name] = value

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test environment for a GroupPowerSaveServer.')
    parser.add_argument('--test', 
    type=str, 
    choices=test_classes.keys(), 
    default=PositionUpdateTest.__name__,
    help='Name of the test function')
    parser.add_argument('--target_server', 
    type=str,
    default='http://localhost:8080/')
    parser.add_argument('--num_clients',
    help='Number of mock clients that you want to spawn',
    type=int,
    default=10)

    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(execute(loop, test_classes[args.test], args.num_clients, args.target_server))
    loop.close()