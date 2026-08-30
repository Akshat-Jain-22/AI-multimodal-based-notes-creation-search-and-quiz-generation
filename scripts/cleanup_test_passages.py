from build_search_index import get_vectorstore

vs = get_vectorstore()
all_ids = vs.get()["ids"]
ids_to_delete = [i for i in all_ids if i.startswith("basic_electronics_test::")]

if ids_to_delete:
    vs.delete(ids=ids_to_delete)
    print(f"Deleted {len(ids_to_delete)} test passages.")
else:
    print("No test passages found — nothing to delete.")

remaining = vs.get()["ids"]
print(f"{len(remaining)} passages remain.")
lecture_ids = sorted(set(i.split("::")[0] for i in remaining))
print(f"Lectures still indexed: {', '.join(lecture_ids)}")