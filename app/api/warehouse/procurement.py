import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.inventory import InventoryTransaction, SparePart

router = APIRouter()


@router.get("/pending", tags=["Procurement Operations"])
async def get_pending_purchase_orders(db: AsyncSession = Depends(get_db)):
    """
    Fetches all Purchase Orders with status 'pending' from PostgreSQL.
    Joins with SparePart to include part name and SKU in the response.
    """
    result = await db.execute(
        select(InventoryTransaction)
        .where(
            InventoryTransaction.transaction_type == "PO_DRAFT",
            InventoryTransaction.status == "pending"
        )
        .options(selectinload(InventoryTransaction.part))
        .order_by(InventoryTransaction.timestamp.desc())
    )
    transactions = result.scalars().all()

    pending_pos = []
    for txn in transactions:
        pending_pos.append({
            "id": str(txn.id),
            "part_name": txn.part.name if txn.part else "Unknown Part",
            "sku": txn.part.sku if txn.part else "N/A",
            "quantity": txn.quantity,
            "urgency": txn.urgency,
            "status": txn.status,
            "timestamp": txn.timestamp.isoformat() if txn.timestamp else None,
        })

    return {"status": "success", "count": len(pending_pos), "data": pending_pos}


@router.put("/{po_id}/approve", tags=["Procurement Operations"])
async def approve_purchase_order(
    po_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Approves a pending Purchase Order."""
    result = await db.execute(
        select(InventoryTransaction).where(InventoryTransaction.id == po_id)
    )
    txn = result.scalar_one_or_none()

    if not txn:
        raise HTTPException(status_code=404, detail="Purchase Order not found.")

    if txn.status != "pending":
        raise HTTPException(status_code=400, detail=f"PO is already '{txn.status}'. Cannot approve.")

    txn.status = "approved"
    await db.commit()

    return {
        "status": "success",
        "message": f"Purchase Order {po_id} approved successfully."
    }


@router.put("/{po_id}/reject", tags=["Procurement Operations"])
async def reject_purchase_order(
    po_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Rejects a pending Purchase Order."""
    result = await db.execute(
        select(InventoryTransaction).where(InventoryTransaction.id == po_id)
    )
    txn = result.scalar_one_or_none()

    if not txn:
        raise HTTPException(status_code=404, detail="Purchase Order not found.")

    if txn.status != "pending":
        raise HTTPException(status_code=400, detail=f"PO is already '{txn.status}'. Cannot reject.")

    txn.status = "rejected"
    await db.commit()

    return {
        "status": "success",
        "message": f"Purchase Order {po_id} rejected."
    }
