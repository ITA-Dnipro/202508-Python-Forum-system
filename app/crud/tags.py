from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.topic import Tag

async def get_or_create_tags_by_name(
    db: AsyncSession, 
    tag_names: List[str]
) -> List[Tag]:
    """
    Takes a list of tag names, retrieves existing tags from the database,
    and creates any that do not already exist.
    """
    
    if not tag_names:
        return []
        
    unique_names = list(set(tag_names))

    result = await db.execute(
        select(Tag).where(Tag.name.in_(unique_names))
    )
    existing_tags = result.scalars().all()
    
    existing_tags_map = {tag.name: tag for tag in existing_tags}

    final_tags_list = []
    
    for name in unique_names:
        if name in existing_tags_map:
            final_tags_list.append(existing_tags_map[name])
        else:
            new_tag = Tag(name=name)
            db.add(new_tag)
            final_tags_list.append(new_tag)
     
    return final_tags_list