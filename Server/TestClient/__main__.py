from .test_client import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test environment for a GroupPowerSaveServer.')
    parser.add_argument('--test', 
    type=str, 
    choices=test_classes.keys(), 
    default=RoleUpdateTest.__name__,
    help='Name of the test function')
    parser.add_argument('--target_server', 
    type=str,
    default='http://localhost:8080/')
    parser.add_argument('--num_clients',
    type=int,
    default=10)

    args = parser.parse_args()

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.get_event_loop()

    if loop.is_running():
        asyncio.ensure_future(execute(loop, test_classes[args.test], args.num_clients, args.target_server), loop=loop)
    else:
        loop.run_until_complete(execute(loop, test_classes[args.test], args.num_clients, args.target_server))
        loop.close()