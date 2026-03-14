from sys import argv
from utils import ASN, check_ISP, make_pppoe_reconnection

def main(FORCE=False, ASN=ASN):
    ISP = check_ISP()
    #No providing ASN, no --force, exit.
    if ASN is None and not FORCE:
        print("No ASN provided, exiting.")
        print("Try running the script with -f or --force flag or provide an ASN with the -a or --asn flag.")
        exit(1)

    while not ISP.startswith(f"{ASN}"):
        print(f"Current ISP: {ISP}")
        make_pppoe_reconnection()
        ISP = check_ISP()
        print(f"ISP after reconnection: {ISP}")
        if ISP.startswith(f"{ASN}"):
            print("Successfully switched to the desired ASN.")
        if FORCE:
            print("Forced reconnection completed.")
            break

if __name__ == "__main__":
    if len(argv) == 1:
        main()
    else:
        match argv[1]:
            case "-f" | "--force":
                print("Forcing PPPoE reconnection...")
                main(FORCE=True)
            case "-a" | "--asn":
                if len(argv) < 3:
                    print("Please provide an ASN after the -a or --asn flag.")
                    exit(1)
                main(FORCE=False, ASN=argv[2])