import os
import glob

def main():
    folder = os.path.abspath("../FrameCreation/Frames")
    files = glob.glob(os.path.join(folder, "frame_*.jpg"))
    if not files:
        print("Aucun fichier à supprimer.")
        return

    for f in files:
        os.remove(f)

    print(f"{len(files)} fichiers supprimés.")

if __name__ == "__main__":
    main()

