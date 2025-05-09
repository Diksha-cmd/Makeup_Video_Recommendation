#!/usr/bin/env python
# coding: utf-8

# In[29]:


import sqlite3
import sys, cv2
sys.path.insert(0, "/Users/dikshatiwari/Documents/Youtube_search/")
import Faceshape_Pipeline as fp


# In[70]:


def recommend_videos(faceshape, ethnicity=None, database_name='youtube.db', top_n=50):
    """
    Recommends the top N video URLs based on likes, comments, and views
    for channels matching the given faceshape and ethnicity.

    Args:
        faceshape (str): The face shape to filter by.
        ethnicity (str): The ethnicity to filter by.
        database_name (str, optional): The name of the SQLite database file.
                                       Defaults to 'your_database.db'.
        top_n (int, optional): The number of top videos to return. Defaults to 50.

    Returns:
        list: A list of the top N video URLs, ordered by a weighted score
              of likes, comments, and views (descending). Returns an empty
              list if no matching channels or videos are found.
    """
    faceshape = faceshape.lower()
    ethnicity = ethnicity.lower()
    ethnicity = ethnicity.replace('\u00a0', ' ')
    print(faceshape, ethnicity)
    conn = None

    try:
        conn = sqlite3.connect(database_name)
        cursor = conn.cursor()

        # 1. Get channel IDs with matching faceshape and ethnicity
        if ethnicity is None or len(ethnicity) ==0:
            print("inside ethnicity none")
            print("faceshape :", faceshape)
            cursor.execute(
                "SELECT channel_id FROM Channels WHERE lower(face_shape) LIKE ? ",
                (faceshape,),
            )
            print("inside ethnicity none")
        else:
            cursor.execute(
                "SELECT channel_id FROM Channels WHERE lower(face_shape) = ? AND lower(ethnicity) LIKE ? ",
                (faceshape, ethnicity),
            )
        matching_channels = cursor.fetchall()

        if not matching_channels:
            print(f"No channels found with faceshape '{faceshape}' and ethnicity '{ethnicity}'.")
            return []

        channel_ids = [channel[0] for channel in matching_channels]
        print("num channles found: ",len(channel_ids))
        channel_id_placeholders = ','.join(['?'] * len(channel_ids))

        # 2. Filter video URLs for those channel IDs and calculate a recommendation score
        # You might need to adjust the weightings (0.6, 0.3, 0.1) based on your preference
        cursor.execute(
            f"""
            SELECT url, likes * 0.6 + comments * 0.3 + views * 0.1 AS score
            FROM Videos
            WHERE channel_id IN ({channel_id_placeholders}) AND LOWER(CONCAT(title, description, tags)) LIKE '% natural makeup%'
            ORDER BY score DESC
            LIMIT ?
            """,
            channel_ids + [top_n],
        )
        top_videos = cursor.fetchall()
        if not top_videos:
            print("No videos found for the matching channels.")
            return []

        return [video[0] for video in top_videos]

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()


# In[72]:


if __name__ == "__main__":
    # target_faceshape = input("Enter the desired face shape: ")
    # target_ethnicity = input("Enter the desired ethnicity: ")
    import sys, json,os
    if len(sys.argv) < 2:
        print("Usage: python faceshape_pipeline.py <image_path>")
        sys.exit(0)
    path = "/Users/dikshatiwari/.cache/kagglehub/datasets/niten19/face-shape-dataset/versions/2/FaceShape Dataset/training_set/round"
    ls = os.listdir(path)
    img = cv2.imread(path+"/"+ls[1])
    predictor = fp.FaceShapePredictor()          # loads model
    result = predictor.predict(img)
    print(json.dumps(result, indent=2))
    print(result["face_shape"])
    s = 'south asian/indian'
    target_faceshape = result["face_shape"]
    # target_ethnicity = "South Asian/Indian"

    recommended_urls = recommend_videos(result["face_shape"],s)


    if recommended_urls:
        print(f"\nTop {len(recommended_urls)} recommended video URLs for channels with face shape '{target_faceshape}' and ethnicity '{target_ethnicity} ':")
        for i, url in enumerate(recommended_urls):
            print(f"{i+1}. {url}")
    else:
        print("No recommended videos found based on your criteria.")




