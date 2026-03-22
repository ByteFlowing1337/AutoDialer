from apis import tplink_api

router = tplink_api.TPLinkAPI()
stok = router.stok
print(f"Stok: {stok}")