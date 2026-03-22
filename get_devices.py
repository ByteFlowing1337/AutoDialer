import apis

def main():
    router = apis.TPLinkAPI()
    devices = router.get_connected_devices()
    print(f"Connected devices:{devices}")
    
if __name__ == "__main__":
    main()