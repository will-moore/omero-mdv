// datasources is the data model - updated via AJAX when user updates form
class DataModel extends EventTarget {

    // each table item is {id: {columns:[], etc} }
    omero_tables = []
    // map-anns, datasets, tags etc have columns in mdv format
    // but the data is not ordered
    unordered_data = []

    // Expect a single Table, which is "ordered"
    // tableData has mdv "columns"
    addTable(tableId, tableData) {
      console.log("test addTable...")
      tableData = this.convertBinayData(tableData);
      tableData.id = tableId
      this.omero_tables.push(tableData);
      this.sortMapAnns();
      this.dispatchEvent(new CustomEvent("dataAdded", {}));
    }

    removeTable(tableId) {
      this.omero_tables = this.omero_tables.filter(table => table.id != tableId);
      this.sortMapAnns();
      this.dispatchEvent(new CustomEvent("dataAdded", {}));
    }

    // Handles "unordered" data: Map-Anns and Datasets
    // tableData has mdv "columns"
    addMapAnns(sourceId, tableData) {
      console.log("ADD MAP-ANNS! ", tableData)
      tableData.id = sourceId
      tableData = this.convertBinayData(tableData);
      // sort according to OMERO.tables (if loaded)
      this.unordered_data.push(tableData);
      this.sortMapAnns();
      this.dispatchEvent(new CustomEvent("dataAdded", {}));
    }

    removeMapAnns(sourceId) {
      this.unordered_data = this.unordered_data.filter(table => table.id != sourceId);
      this.dispatchEvent(new CustomEvent("dataAdded", {}));
    }

    sortMapAnns() {
      let pk_name = "Image"
      // If we have any OMERO.tables, use the first 'Image' column as a primary key
      const pk_column = this.omero_tables.flatMap(ds => ds.columns).find(col => col.name == pk_name)
      this.unordered_data.forEach(data => {
        // make a dict so we can pick rows by ID
        const key_column = data.columns.find(col => col.name == pk_name);
        let pk_ids;
        if (pk_column) {
          pk_ids = [...pk_column.data];
        } else {
          pk_ids = [...key_column.data];
          pk_ids.sort();
        }
        if (key_column) {
          let rowsById = {};
          key_column.rowData.forEach((pk, index) => {
            let row = data.columns.map(col => col.rowData[index]);
            rowsById[pk] = row;
          });
          let sortedRows = pk_ids.map(pk => {
            return rowsById[pk];
          });
          data.columns.forEach((col, idx) => {
            let rowData = sortedRows.map(row => row[idx]);
            col.rowData = rowData;
          });
        }
      });
    }

    getColumns() {
      let cols = [this.omero_tables, this.unordered_data].flatMap(dsrc => dsrc.flatMap(ds => ds.columns));
      return cols;
    }

    getNumberColumns() {
        return this.getColumns().filter(col => col.datatype == "double" || col.datatype == "integer")
    }

    getStringColumns() {
        return this.getColumns().filter(col => col.datatype == "text" || col.datatype == "multitext")
    }

    convertBinayData(tableData) {
      tableData.columns.forEach(col => {
        col.rowData = this.getVals(col);
      })
      return tableData;
    }

    getVals(column) {
      if (column.datatype == "double" || column.datatype == "integer") {
        return column.data;
      }
      if (column.datatype == "text") {
        return column.data.map(idx => idx == 65535 ? "" : column.values[idx]);
      }
      if (column.datatype == "multitext") {
        let colData = [];
        let rowCount = column.data.length / column.stringLength;
        for (let rowIndex=0; rowIndex < rowCount; rowIndex++) {
          let offset = rowIndex * column.stringLength;
          let indicies = column.data.slice(offset, offset + column.stringLength);
          let rowVal = indicies.map(idx => idx == 65535 ? "" : column.values[idx]).filter(Boolean).join(", ");
          colData.push(rowVal);
        }
      }
      return "";
    }

    // Used for rendering into html table, were we want to get a row at a time
    getRowData() {
      const cols = this.getColumns();
      if (cols.length == 0) {
        return [];
      }
      let primaryKeys = cols[0].data;
      let rowsData = primaryKeys.map((pk, index) => {
        // TODO - sort unordered data by primary key
        let row = cols.map(col => col.rowData[index]);
        return row;
      });
      return rowsData;
    }
  }
